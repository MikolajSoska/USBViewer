import glob
from typing import List, Iterator

import utils
from device import USBDevice
from viewer.base import BaseViewer


class LinuxViewer(BaseViewer):

    def get_usb_devices(self) -> List[USBDevice]:
        pass

    @staticmethod
    def __get_log_sections() -> Iterator[List[str]]:
        for log_path in sorted(glob.glob('/var/log/syslog*'), reverse=True):  # Sort to start reading from oldest file
            for section in utils.parse_linux_log_file(log_path):
                yield section
