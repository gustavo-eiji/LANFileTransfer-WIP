from device import Device

class DeviceManager:

    def __init__(self) -> None:
        self.devices: dict[str, Device] = {}
        self.service_names: dict[str, str] = {}

    def add_device(self, service_name: str, device: Device) -> None:
        self.devices[device.device_id] = device
        self.service_names[service_name] = device.device_id

    def remove_device(self, service_name: str) -> None:

        device_id = self.service_names.pop(service_name, None)

        if device_id is None:
            return

        self.devices.pop(device_id, None)

    def get_devices(self) -> list[Device]:
        return list(self.devices.values())


