from dataclasses import dataclass

@dataclass
class Device:
    device_id: str
    hostname: str
    ip_address: str
    port: int
    operating_system: str
    version: str
    is_local: bool = False