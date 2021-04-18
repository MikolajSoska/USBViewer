import abc
from typing import List

from device import USBDevice


class BaseViewer(abc.ABC):

    @abc.abstractmethod
    def get_usb_devices(self) -> List[USBDevice]:
        pass
