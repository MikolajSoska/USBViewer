import winreg
from typing import List, Tuple, Dict, Any, Optional

import utils
from device import USBDevice


class WindowsViewer:
    __USBSTOR_PATH = r'SYSTEM\CurrentControlSet\Enum\USBSTOR'
    __USB_PATH = r'SYSTEM\CurrentControlSet\Enum\USB'
    __MOUNTED_DEVICES_PATH = r'SYSTEM\MountedDevices'

    def __init__(self):
        self.__registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    def __del__(self):
        self.__registry.Close()

    def get_usb_devices(self) -> List[USBDevice]:
        usb_devices = self.__get_base_device_info()
        self.__set_usb_registry_info(usb_devices)
        self.__set_mounted_devices_registry_info(usb_devices)

        return usb_devices

    def __get_base_device_info(self) -> List[USBDevice]:
        root_key = winreg.OpenKey(self.__registry, WindowsViewer.__USBSTOR_PATH)
        usbstor_keys = self.__get_registry_keys(root_key)
        usb_devices = []

        for key_str in usbstor_keys:
            device_attributes = self.__parse_device_name(key_str)
            if device_attributes is None:
                continue

            vendor, product, version = device_attributes
            usb_path = rf'{WindowsViewer.__USBSTOR_PATH}\{key_str}'
            usb_key = winreg.OpenKey(self.__registry, usb_path)
            devices_keys = self.__get_registry_keys(usb_key)
            for device in devices_keys:
                device_key = winreg.OpenKey(self.__registry, rf'{usb_path}\{device}')
                device_values = self.__get_registry_values(device_key)
                serial_number = device.split('&')[0]
                friendly_name = device_values['FriendlyName']
                if 'ParentPrefixId' in device_values:
                    parent_prefix_id = device_values['ParentPrefixId']
                else:
                    parent_prefix_id = device

                usb_device = USBDevice(vendor, product, version, serial_number, friendly_name, parent_prefix_id)
                usb_devices.append(usb_device)

        return usb_devices

    def __set_usb_registry_info(self, usb_devices: List[USBDevice]) -> None:
        root_key = winreg.OpenKey(self.__registry, WindowsViewer.__USB_PATH)
        device_ids = self.__get_registry_keys(root_key)
        device_dict = {}
        for device_id in device_ids:
            if 'VID' not in device_id or 'PID' not in device_id:
                continue

            device_key = winreg.OpenKey(self.__registry, rf'{WindowsViewer.__USB_PATH}\{device_id}')
            serial_number = self.__get_registry_keys(device_key)[0]
            device_dict[serial_number] = device_id

        for device in usb_devices:
            for serial_number, device_id in device_dict.items():
                if device.serial_number != serial_number:
                    continue

                device_info = device_id.split('&')
                device.vendor_id = device_info[0].replace('VID_', '')
                device.product_id = device_info[1].replace('PID_', '')

    def __set_mounted_devices_registry_info(self, usb_devices: List[USBDevice]) -> None:
        root_key = winreg.OpenKey(self.__registry, WindowsViewer.__MOUNTED_DEVICES_PATH)
        registry_values = self.__get_registry_values(root_key)

        for device in usb_devices:
            for key, value in registry_values.items():
                value = utils.convert_binary_to_ascii_string(value)
                if device.parent_prefix_id not in value:
                    continue

                if r'\Volume' in key:
                    guid_start_index = key.index('{')
                    device.guid = key[guid_start_index:]
                elif r'\Dos' in key:
                    letter_start_index = key.rindex('\\')
                    device.drive_letter = key[letter_start_index + 1:]

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
        values_dict = {}

        for index in range(values_length):
            name, value, _ = winreg.EnumValue(root_key, index)
            values_dict[name] = value

        return values_dict
