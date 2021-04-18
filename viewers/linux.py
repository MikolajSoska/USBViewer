import glob
from typing import List, Iterator, Optional

import utils
from device import USBDevice, USBDeviceLinux
from viewers.base import BaseViewer


class LinuxViewer(BaseViewer):
    def get_usb_devices(self) -> List[USBDevice]:
        usb_devices = []
        for section in self.__get_log_sections():
            device = USBDeviceLinux()
            device.vendor_id = self.__get_device_id_by_type(section[0], 'idVendor')
            device.product_id = self.__get_device_id_by_type(section[0], 'idProduct')
            device.version = self.__get_device_id_by_type(section[0], 'bcdDevice')
            device.syslog_product = self.__get_device_info_from_section(section, 'Product:')
            device.syslog_manufacturer = self.__get_device_info_from_section(section, 'Manufacturer:')
            device.serial_number = self.__get_device_info_from_section(section, 'SerialNumber:')
            device.friendly_name = self.__get_device_info_from_section(section, 'Direct-Access')

            usb_devices.append(device)

        return usb_devices

    @staticmethod
    def __get_log_sections() -> Iterator[List[str]]:
        for log_path in sorted(glob.glob('/var/log/syslog*'), reverse=True):  # Sort to start reading from oldest file
            for section in utils.parse_linux_log_file(log_path):
                yield section

    @staticmethod
    def __get_device_id_by_type(string: str, id_type: str) -> str:
        index_start = string.index(id_type)
        if ',' in string[index_start:]:
            index_end = string.index(',', index_start)
        else:
            index_end = len(string)

        device_id = string[index_start:index_end]
        device_id = device_id.replace(f'{id_type}=', '')
        device_id = device_id.strip()

        return device_id

    @staticmethod
    def __get_device_info_from_section(section: List[str], info_type: str) -> Optional[str]:
        for line in section:
            if info_type in line:
                start_index = line.index(info_type)
                print(line[start_index + len(info_type):])
                return line[start_index + len(info_type):].split(maxsplit=1)[-1].strip()
        return None
