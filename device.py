from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(init=True, repr=True, eq=False)
class USBDevice:
    vendor: str
    product: str
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
