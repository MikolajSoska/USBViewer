from dataclasses import dataclass
from typing import Optional


@dataclass(init=True, repr=True, eq=False)
class USBStorage:
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
