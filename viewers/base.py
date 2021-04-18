import abc
from typing import List

import utils
from device import USBDevice


class BaseViewer(abc.ABC):

    @abc.abstractmethod
    def get_usb_devices(self) -> List[USBDevice]:
        pass

    @staticmethod
    def _set_devices_info(usb_devices: List[USBDevice]) -> None:
        for device in usb_devices:
            if device.vendor_id is not None and device.product_id is not None:
                vendor_name, product_description = utils.get_device_info_from_web(device.vendor_id, device.product_id)
                device.vendor_name = vendor_name
                device.product_description = product_description
