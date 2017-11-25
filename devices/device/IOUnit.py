import json
from time import time

class IOUnit:
        @staticmethod
        def get_name_from_topic(topic):
            return topic.split("/")[1]

        @staticmethod
        def find():
            return "home/+/info/status"

        def __init__(self, name, mqtt):
            self.name = name
            self.mqtt = mqtt
            self.info = dict()
            self.io_state = dict()
            self.error_log = dict()

        def get_name(self):
            return self.name

        def get_type(self):
            return self.__class__.__name__

        def start_update(self):
            self.mqtt.subscribe("home/{}/info/+".format(self.name), self._mqtt_update_info)
            self.mqtt.subscribe("commands/home/{}/+/output".format(self.name), self._mqtt_update_io_request)
            self.mqtt.subscribe("home/{}/+/output".format(self.name), self._mqtt_update_io_state)

        def _mqtt_update_info(self, topic, payload):
            prop = topic.split("/")[-1]
            self.info[prop] = payload

        def _mqtt_update_io_state(self, topic, payload):
            io = topic.split("/")[-2]

            try:
                res = json.loads(payload)
            except ValueError:
                raise RuntimeError("Malformated json from node {}: {}".format(self.name, payload))

            try:
                if res["status"] in ["ok", "OK", "Ok"]:
                    value = res["value"]
                else:
                    s = "Received a failed set-io command on io '{}' from node '{}'".format(io, self.name)
                    self.error_log[time()] = s
                    print(s)
            except KeyError:
                raise RuntimeError("Missing key in IOUnit output result: {}".format(payload))

            self._set_io_state(io, value)

        def _mqtt_update_io_request(self, topic, payload):
            io = topic.split("/")[-2]
            self._set_io_state(io, payload, synced=False)

        '''
        Set requested value if synced = 0,
        actual value of synced = True
        '''
        def _set_io_state(self, io, value, synced=True):
            field = "actual" if synced else "requested"

            if not hasattr(self.io_state, io):
                self.io_state[io] = dict()

            if value == "on":
                self.io_state[io][field] = True
            elif value == "off":
                self.io_state[io][field] = False
            else:
                raise RuntimeError("Got unknown IO state '{}' from IOUnit {}".format(value, io))
