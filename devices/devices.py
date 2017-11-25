
class DeviceManager:

    def __init__(self, mqtt):
        self.mqtt = mqtt

        self.device_table = dict()

    def add_device(self, device):
        name = device.get_name()
        if not name in self.device_table.keys():
            print("Added device '{}' of type '{}'".format(name, device.get_type()))
            self.device_table[name] = device
            device.start_update()
