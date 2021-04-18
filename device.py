from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(init=True, repr=True, eq=False)
class USBDevice:
    usbstor_vendor: str
    usbstor_product: str
    version: str
    serial_number: str
    friendly_name: str
    parent_prefix_id: str
    vendor_id: Optional[str] = None
    product_id: Optional[str] = None
    guid: Optional[str] = None
    drive_letter: Optional[str] = None
    first_connect_date: Optional[datetime] = None
    last_connect_date: Optional[datetime] = None
    vendor_name: Optional[str] = None
    product_description: Optional[str] = None

    def get_details(self) -> str:
        details = f'Device: {self.friendly_name}\n'
        details += 'Details:\n'
        details += f'\t- Vendor Name: {self.vendor_name}\n'
        details += f'\t- Product Description: {self.product_description}\n'
        details += f'\t- USBSTOR Vendor: {self.usbstor_vendor}\n'
        details += f'\t- USBSTOR Product: {self.usbstor_product}\n'
        details += f'\t- First Connect Date: {self.first_connect_date}\n'
        details += f'\t- Last Connect Date: {self.last_connect_date}\n'
        details += f'\t- Serial Number: {self.serial_number}\n'
        details += f'\t- Vendor ID: {self.vendor_id}\n'
        details += f'\t- Product ID: {self.product_id}\n'
        details += f'\t- Drive Letter: {self.drive_letter}\n'
        details += f'\t- Version: {self.version}\n'
        details += f'\t- GUID: {self.guid}\n'
        details += f'\t- Parent Prefix ID: {self.parent_prefix_id}\n'

        return details
