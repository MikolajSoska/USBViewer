import glob
import os
import platform
from datetime import datetime
from typing import List, Tuple, Iterator, Optional

import utils
from device import USBDevice, USBDeviceLinux
from viewers.base import BaseViewer


class LinuxViewer(BaseViewer):
    def __init__(self):
        self.__hostname = platform.node()

    def get_usb_devices(self) -> List[USBDevice]:
        usb_devices = []
        for section, year in self.__get_log_sections():
            serial_number = self.__get_device_info_from_section(section, 'SerialNumber:')
            connect_time = self.__get_device_connect_time(section[0], year)
            device = self.__get_device_if_exist(usb_devices, serial_number)
            if device is not None:
                # Log messages are in chronological order so last time is updated
                device.last_connect_date = connect_time
                continue

            device = USBDeviceLinux(
                serial_number=serial_number,
                first_connect_date=connect_time,
                last_connect_date=connect_time
            )

            device.vendor_id = self.__get_device_id_by_type(section[0], 'idVendor')
            device.product_id = self.__get_device_id_by_type(section[0], 'idProduct')
            device.version = self.__get_device_id_by_type(section[0], 'bcdDevice')
            device.syslog_product = self.__get_device_info_from_section(section, 'Product:')
            device.syslog_manufacturer = self.__get_device_info_from_section(section, 'Manufacturer:')
            device.serial_number = self.__get_device_info_from_section(section, 'SerialNumber:')
            device.friendly_name = self.__get_device_info_from_section(section, 'Direct-Access')
            device.device_size = self.__get_device_size(section)

            usb_devices.append(device)

        return usb_devices

    def __get_log_sections(self) -> Iterator[Tuple[List[str], int]]:
        for log_path in sorted(glob.glob('/var/log/syslog*'), reverse=True):  # Sort to start reading from oldest file
            # In log there is no year in timestamp, so this value will be used
            year = self.__get_file_last_modification_year(log_path)
            for section in utils.parse_linux_log_file(log_path):
                yield section, year

    @staticmethod
    def __get_file_last_modification_year(filepath: str) -> int:
        timestamp = os.stat(filepath).st_mtime
        return datetime.fromtimestamp(timestamp).year

    def __get_device_connect_time(self, string: str, year: int) -> datetime:
        end_index = string.index(self.__hostname)
        connect_time = string[:end_index].strip()
        connect_time = f'{year}-{connect_time}'
        return datetime.strptime(connect_time, '%Y-%b %d %H:%M:%S')

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
                return line[start_index + len(info_type):].split(maxsplit=1)[-1].strip()
        return None

    @staticmethod
    def __get_device_size(section: List[str]) -> Optional[str]:
        for line in section:
            if 'logical blocks' in line:
                index_start = line.rindex(']')
                return line[index_start + 1:].strip()
        return None

    @staticmethod
    def __get_device_if_exist(usb_devices: List[USBDeviceLinux], serial_number: str) -> Optional[USBDeviceLinux]:
        for device in usb_devices:
            if device.serial_number == serial_number:
                return device
        return None
