import winreg
from typing import List, Tuple, Dict, Any, Optional

from model import USBStorage


class WindowsViewer:
    __USBSTOR_PATH = r'SYSTEM\CurrentControlSet\Enum\USBSTOR'

    def get_usb_devices(self) -> List[USBStorage]:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        root_key = winreg.OpenKey(registry, WindowsViewer.__USBSTOR_PATH)
        usbstor_keys = self.__get_registry_keys(root_key)
        usb_devices = []

        for key_str in usbstor_keys:
            device_attributes = self.__parse_device_name(key_str)
            if device_attributes is None:
                continue

            vendor, product, version = device_attributes
            usb_path = rf'{WindowsViewer.__USBSTOR_PATH}\{key_str}'
            usb_key = winreg.OpenKey(registry, usb_path)
            devices_keys = self.__get_registry_keys(usb_key)
            for device in devices_keys:
                device_key = winreg.OpenKey(registry, rf'{usb_path}\{device}')
                device_values = self.__get_registry_values(device_key)
                serial_number = device.split('&')[0]
                friendly_name = device_values['FriendlyName']

                usb_device = USBStorage(vendor, product, version, serial_number, friendly_name)
                usb_devices.append(usb_device)

        return usb_devices

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

    @staticmethod
    def __parse_device_name(device_name: str) -> Optional[Tuple[str, str, str]]:
        name_split = device_name.split('&')
        if len(name_split) != 4 or name_split[0].lower() != 'disk':
            return None

        vendor = name_split[1].replace('Ven_', '')
        product = name_split[2].replace('Prod_', '')
        version = name_split[3].replace('Rev_', '')

        return vendor, product, version
