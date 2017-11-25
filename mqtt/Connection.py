import paho.mqtt.client as mqtt
import sys
from time import time, sleep
from threading import Lock

from topic_matcher import topic_matches_sub
from .. import log
from ..utils import get_mac, rand_str

'''
callback for paho on mqtt message
'''
def dispatch(client, data, msg):
    cb_lst = []
    data.dtlock.acquire()
    try:
        for sub, callback in data.dispatch_table.iteritems():
            if topic_matches_sub(sub, msg.topic):
                cb_lst.append(callback)
    finally:
        data.dtlock.release()

    if not len(cb_lst):
        raise RuntimeError("Dispatch table failed to match topic", topic)
    else:
        [callback(msg.topic, str(msg.payload.decode("utf-8"))) for callback in cb_lst]

'''
callback for paho on mqtt connected
'''
def on_connect(client, data, flags, rc):
    if rc == 0:
        data.publish({data.path + "/info/status" : "online"})
        log("Connected")
        return

    log("Connection failed with status " + str(rc))
    data.connected = False
    sleep(data.retry_time)
    data.retry_time = min(data.max_retry_time, data.retry_time*2)
    data.try_connect()


'''
callback for paho on mqtt disconnect
'''
def on_disconnect(client, data, rc):
    log("Disconnected with reason {}...".format(rc))
    data.connected = False
    if rc != 0:
        data.try_connect()


class Mqtt:
    def __init__(self, config):
        self.id = "{}-{}".format(get_mac(), rand_str(10))
        self.connected = False
        self.min_retry_time = float(config["min_retry_time"])
        self.max_retry_time = float(config["max_retry_time"])
        self.retry_time = self.min_retry_time
        self.server = config['server']

        banned = "/#+"
        self.node_name = "".join(["-" if ch in banned else ch for ch in config['node_name']])

        self.path = "home/{name}/{mac}".format(name=self.node_name, mac=get_mac())

        self.mqttc = mqtt.Client(client_id=self.id, clean_session=True, userdata=self)
        self.mqttc.will_set(
                topic=self.path + "/info/status",
                payload="lost",
                qos=1,
                retain=True)

        self.mqttc.on_message = dispatch
        self.mqttc.on_connect = on_connect
        self.mqttc.on_disconnect = on_disconnect

        self.dispatch_table = dict()
        self.dtlock = Lock()


    '''
    Connect to MQTT and block until keyboard interrupt
    '''
    def connect_and_block(self):
        self.connect()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect()

    '''
    Connect to MQTT
    '''
    def connect(self):
        self.try_connect()
        self.mqttc.loop_start()

    '''
    Disconnect from MQTT
    '''
    def disconnect(self):
        self.publish({self.path + "/info/status" : "disconnected"})
        sleep(0.5)
        self.mqttc.disconnect()
        self.mqttc.loop_stop()

    '''
    Add a topic and a callback for subscription
    '''
    def subscribe(self, topic, callback, qos=1):
        self.dtlock.acquire()
        try:
            if not topic in self.dispatch_table:
                self.mqttc.subscribe(topic, qos)
            self.dispatch_table[topic] = callback
        finally:
            self.dtlock.release()

    '''
    True if the topic matches the subscription
    '''
    def topic_matches_sub(self, topic, sub):
        return topic_matches_sub(sub, topic)

    '''
    publish a dict with topic, message pairs
    '''
    def publish(self, data, retain=False, qos=1):
        data[self.path + "/info/last_update"] = str(time())
        for key, value in data.iteritems():
            self.mqttc.publish(
                    topic=key,
                    payload=value,
                    qos=qos,
                    retain=retain)

    '''
    get mqtt id
    '''
    def get_id(self):
        return self.id


    '''
    try to connect to mqtt server
    '''
    def try_connect(self):
        while not self.connected:
            try:
                self.mqttc.connect(self.server, keepalive=25)
                self.connected = True
            except socket.error:
                log("Failed to connect... Retrying in {} seconds".format(self.retry_time))
                sleep(self.retry_time)
