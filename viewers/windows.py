import glob
import winreg
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

import utils
from device import USBDevice, USBDeviceWindows
from viewers.base import BaseViewer


class WindowsViewer(BaseViewer):
    __USBSTOR_PATH = r'SYSTEM\CurrentControlSet\Enum\USBSTOR'
    __USB_PATH = r'SYSTEM\CurrentControlSet\Enum\USB'
    __MOUNTED_DEVICES_PATH = r'SYSTEM\MountedDevices'
    __PORTABLE_DEVICES_PATH = r'SOFTWARE\Microsoft\Windows Portable Devices\Devices'
    __MOUNT_POINTS_PATH = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2'

    def __init__(self):
        self.__machine_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        self.__user_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)

    def __del__(self):
        self.__machine_registry.Close()
        self.__user_registry.Close()

    def get_usb_devices(self) -> List[USBDevice]:
        usb_devices = self.__get_base_device_info()
        self.__set_vendor_and_product_ids(usb_devices)
        self.__set_guids(usb_devices)
        self.__set_drive_letters(usb_devices)
        self.__set_first_connect_dates(usb_devices)
        self.__set_last_connect_dates(usb_devices)
        self.__set_devices_info(usb_devices)

        return usb_devices

    def __get_base_device_info(self) -> List[USBDeviceWindows]:
        root_key = winreg.OpenKey(self.__machine_registry, WindowsViewer.__USBSTOR_PATH)
        usbstor_keys = self.__get_registry_keys(root_key)
        usb_devices = []

        for key_str in usbstor_keys:
            device_attributes = self.__parse_device_name(key_str)
            if device_attributes is None:
                continue

            vendor, product, version = device_attributes
            usb_path = rf'{WindowsViewer.__USBSTOR_PATH}\{key_str}'
            usb_key = winreg.OpenKey(self.__machine_registry, usb_path)
            devices_keys = self.__get_registry_keys(usb_key)
            for device in devices_keys:
                device_key = winreg.OpenKey(self.__machine_registry, rf'{usb_path}\{device}')
                device_values = self.__get_registry_values(device_key)
                serial_number = device.split('&')[0]
                friendly_name = device_values['FriendlyName']
                if 'ParentPrefixId' in device_values:
                    parent_prefix_id = device_values['ParentPrefixId']
                else:
                    parent_prefix_id = device

                usb_device = USBDeviceWindows(
                    usbstor_vendor=vendor,
                    usbstor_product=product,
                    version=version,
                    serial_number=serial_number,
                    friendly_name=friendly_name,
                    parent_prefix_id=parent_prefix_id
                )
                usb_devices.append(usb_device)

        return usb_devices

    def __set_vendor_and_product_ids(self, usb_devices: List[USBDeviceWindows]) -> None:
        root_key = winreg.OpenKey(self.__machine_registry, WindowsViewer.__USB_PATH)
        device_ids = self.__get_registry_keys(root_key)
        device_dict = {}
        for device_id in device_ids:
            if 'VID' not in device_id or 'PID' not in device_id:
                continue

            device_key = winreg.OpenKey(self.__machine_registry, rf'{WindowsViewer.__USB_PATH}\{device_id}')
            serial_number = self.__get_registry_keys(device_key)[0]
            device_dict[serial_number] = device_id

        for device in usb_devices:
            for serial_number, device_id in device_dict.items():
                if device.serial_number != serial_number:
                    continue

                device_info = device_id.split('&')
                device.vendor_id = device_info[0].replace('VID_', '')
                device.product_id = device_info[1].replace('PID_', '')

    def __set_guids(self, usb_devices: List[USBDeviceWindows]) -> None:
        root_key = winreg.OpenKey(self.__machine_registry, WindowsViewer.__MOUNTED_DEVICES_PATH)
        registry_values = self.__get_registry_values(root_key)

        for device in usb_devices:
            for key, value in registry_values.items():
                value = utils.convert_binary_to_ascii_string(value)
                if device.parent_prefix_id not in value:
                    continue

                if r'\Volume' in key:
                    guid_start_index = key.index('{')
                    device.guid = key[guid_start_index:]

    def __set_drive_letters(self, usb_devices: List[USBDeviceWindows]) -> None:
        root_key = winreg.OpenKey(self.__machine_registry, WindowsViewer.__PORTABLE_DEVICES_PATH)
        registry_keys = self.__get_registry_keys(root_key)

        for device in usb_devices:
            for key in registry_keys:
                if device.parent_prefix_id not in key:
                    continue
                device_key = winreg.OpenKey(self.__machine_registry, rf'{WindowsViewer.__PORTABLE_DEVICES_PATH}\{key}')
                values = self.__get_registry_values(device_key)
                device.drive_letter = values['FriendlyName']

    @staticmethod
    def __set_first_connect_dates(usb_devices: List[USBDeviceWindows]) -> None:
        time_dict = {}
        for log_path in glob.glob(r'C:\Windows\inf\setupapi.dev*.log'):  # There could be multiple files in system
            for section in utils.parse_windows_log_file(log_path):
                if 'Device Install ' in section[0] and 'SUCCESS' in section[-1]:
                    install_time = section[-2].split()[-2:]  # Get only date and time from string
                    install_time = ' '.join(install_time)
                    install_time = install_time.split('.')[0]  # Remove milliseconds
                    install_time = datetime.strptime(install_time, '%Y/%m/%d %H:%M:%S')
                    time_dict[section[0]] = install_time

        for device in usb_devices:
            for key, install_time in time_dict.items():
                if device.serial_number in key:
                    device.first_connect_date = install_time

    def __set_last_connect_dates(self, usb_devices: List[USBDeviceWindows]) -> None:
        root_key = winreg.OpenKey(self.__user_registry, WindowsViewer.__MOUNT_POINTS_PATH)
        guids = self.__get_registry_keys(root_key)

        for device in usb_devices:
            for guid in guids:
                if device.guid != guid:
                    continue

                device_key = winreg.OpenKey(self.__user_registry, rf'{WindowsViewer.__MOUNT_POINTS_PATH}\{guid}')
                timestamp = self.__get_registry_timestamp(device_key)
                device.last_connect_date = datetime.fromtimestamp(timestamp)

    @staticmethod
    def __set_devices_info(usb_devices: List[USBDeviceWindows]) -> None:
        for device in usb_devices:
            if device.vendor_id is not None and device.product_id is not None:
                vendor_name, product_description = utils.get_device_info_from_web(device.vendor_id, device.product_id)
                device.vendor_name = vendor_name
                device.product_description = product_description

    @staticmethod
    def __parse_device_name(device_name: str) -> Optional[Tuple[str, str, str]]:
        name_split = device_name.split('&')
        if len(name_split) != 4 or name_split[0] != 'Disk':
            return None

        vendor = name_split[1].replace('Ven_', '')
        product = name_split[2].replace('Prod_', '')
        version = name_split[3].replace('Rev_', '')

        return vendor, product, version

    @staticmethod
    def __get_registry_keys(root_key: winreg.HKEYType) -> List[str]:
        key_info = winreg.QueryInfoKey(root_key)
        keys_length = key_info[0]

        return [winreg.EnumKey(root_key, index) for index in range(keys_length)]

    @staticmethod
    def __get_registry_values(root_key: winreg.HKEYType) -> Dict[str, Any]:
        key_info = winreg.QueryInfoKey(root_key)
        values_length = key_info[1]
        values_dict = defaultdict(lambda: None)

        for index in range(values_length):
            name, value, _ = winreg.EnumValue(root_key, index)
            values_dict[name] = value

        return values_dict

    @staticmethod
    def __get_registry_timestamp(root_key: winreg.HKEYType) -> int:
        key_info = winreg.QueryInfoKey(root_key)
        return utils.convert_windows_time_to_unix(key_info[2])
