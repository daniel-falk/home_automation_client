#from gui import Gui
from mqtt.Connection import Mqtt
from . import conf
#from controlpanel.InterfacePanel import InterfacePanel
from devices.devices import DeviceManager
from devices.explore import DeviceExplorer

# Connect MQTT to broker
mqtt = Mqtt(dict(conf.items("MQTT")))
mqtt.connect()

# Create a DeviceManager - this is used as a shadow register
# to communicate with home automation nodes. The exporer is for automatically
# detect when a new node following a specified standard is connected
devices = DeviceManager(mqtt)
explorer = DeviceExplorer(mqtt, devices)
explorer.find_class("IOUnit")

# Create a panel object for the physical buttons and rotary encoder
#panel = InterfacePanel()

# Create a gui-object which will interact with the panel and our devices
#gui = Gui(panel, devices)
#gui.run()

try:
    while(True):
        pass
except KeyboardInterrupt:
    pass

# Clean-up...
mqtt.disconnect()
