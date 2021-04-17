from dataclasses import dataclass


@dataclass(init=True, repr=True, eq=False)
class USBStorage:
    vendor: str
    product: str
    version: str
    serial_number: str
    friendly_name: str
