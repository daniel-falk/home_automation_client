#from Gui import Gui
from mqtt.Connection import Mqtt
from . import conf

from time import sleep

def cb(topic, message):
    print("Got '{}' on topic '{}'".format(message, topic))

mqtt = Mqtt(dict(conf.items("MQTT")))
mqtt.connect()

mqtt.subscribe("apa/#", cb)

sleep(30)

mqtt.disconnect()

#gui = Gui(Mqtt)
#
#gui.run()
