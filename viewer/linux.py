import glob
from typing import List, Iterator

import utils
from device import USBDevice, USBDeviceLinux
from viewer.base import BaseViewer


class LinuxViewer(BaseViewer):
    def get_usb_devices(self) -> List[USBDevice]:
        usb_devices = []
        for section in self.__get_log_sections():
            device = USBDeviceLinux()
            device.vendor_id = self.get_device_id_by_type(section[0], 'idVendor')
            device.product_id = self.get_device_id_by_type(section[0], 'idProduct')
            device.version = self.get_device_id_by_type(section[0], 'bcdDevice')

            usb_devices.append(device)

        return usb_devices

    @staticmethod
    def __get_log_sections() -> Iterator[List[str]]:
        for log_path in sorted(glob.glob('/var/log/syslog*'), reverse=True):  # Sort to start reading from oldest file
            for section in utils.parse_linux_log_file(log_path):
                yield section

    @staticmethod
    def get_device_id_by_type(string: str, id_type: str) -> str:
        index_start = string.index(id_type)
        if ',' in string[index_start:]:
            index_end = string.index(',', index_start)
        else:
            index_end = len(string)

        device_id = string[index_start:index_end]
        device_id = device_id.replace(f'{id_type}=', '')
        device_id = device_id.strip()

        return device_id
