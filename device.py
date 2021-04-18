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
