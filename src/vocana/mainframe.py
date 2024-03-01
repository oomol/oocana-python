import json
import paho.mqtt.client as mqtt
import operator
from urllib.parse import urlparse
import uuid

class Mainframe:
    address: str
    client: mqtt.Client
    on_ready: bool

    def __init__(self, address: str) -> None:
        self.address = address
        self.on_ready = False

    def connect(self):
        connect_address = self.address if operator.contains(self.address, "://") else operator.concat("mqtt://", self.address)
        url = urlparse(connect_address)

        self.client = mqtt.Client(client_id=str(uuid.uuid4()))
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect_fail = self.on_connect_fail
        self.client.connect(host=url.hostname, port=url.port)
        # self.client.loop_start()
        return self.client

    def on_connect_fail(self, client, userdata, flags, rc):
        print('on_connect_fail')

    def on_disconnect(self, client, userdata, rc):
        self.on_ready = False

    def send(self, msg):
        if self.on_ready == False:
            raise Exception('SDK is not ready')
        session_id = msg.get('session_id')

        info = self.client.publish(
            f'session/{session_id}',
            json.dumps(msg),
            qos=1
        )
        info.wait_for_publish()

    def send_report(self, msg):
        if self.on_ready == False:
            raise Exception('SDK is not ready')
        info = self.client.publish(
            f'report',
            json.dumps(msg),
            qos=1
        )
        info.wait_for_publish()

    def send_ready(self, msg):
        session_id = msg.get('session_id')
        task_id = msg.get('task_id')
        topic = f'input/{session_id}/{task_id}'
        replay = None

        def on_message_once(_client, _userdata, message):
            nonlocal replay
            self.on_ready = True
            self.client.unsubscribe(topic)
            replay = json.loads(message.payload)

        self.client.subscribe(topic, qos=1)
        self.client.message_callback_add(topic, on_message_once)

        self.client.publish(
            f'session/{session_id}',
            json.dumps(msg),
            qos=1
        )

        while True:
            if replay is not None:
                break

        return replay
    
    def subscribe_execute(self, name, callback):
        def on_message(_client, _userdata, message):
            print('subscribe_execute receive message')
            payload = json.loads(message.payload)
            callback(payload)

        topic = f'executor/{name}'
        self.client.subscribe(topic, qos=1)
        self.client.message_callback_add(topic, on_message)

    def loop(self):
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()
