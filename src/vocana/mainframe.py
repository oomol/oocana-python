import json
import paho.mqtt.client as mqtt
import operator
from urllib.parse import urlparse
import uuid
from .data import BlockInfo

name = "python_executor"
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

        self.client = mqtt.Client(client_id=f'python-executor-{uuid.uuid4().hex[:8]}', clean_session=False)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect_fail = self.on_connect_fail
        self.client.connect(host=url.hostname, port=url.port)
        self.client.loop_start()
        return self.client
    
    # https://stackoverflow.com/a/57396505/4770006 在 on_connect 回调里面订阅的 topic，在重连时，会自动重新订阅，其他地方调用 subscribe 需要自己处理重新订阅逻辑。
    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        client.subscribe(f'executor/{name}/execute', qos=1)
        client.subscribe(f'executor/{name}/drop', qos=1)

    def on_connect_fail(self, client, userdata, flags, rc):
        print('on_connect_fail')

    def on_disconnect(self, client, userdata, rc):
        self.on_ready = False

    def send(self, info: BlockInfo, msg):
        if self.on_ready == False:
            raise Exception('SDK is not ready')
        session_id = msg.get('session_id')

        info = self.client.publish(
            f'session/{session_id}',
            json.dumps({**info.dict(), **msg}),
            qos=1
        )
        info.wait_for_publish()

    def report(self, info: BlockInfo, msg: dict):
        if self.on_ready == False:
            raise Exception('SDK is not ready')
        info = self.client.publish(
            f'report',
            json.dumps({**info.dict(), **msg}),
            qos=1
        )
        info.wait_for_publish()

    def notify_ready(self, msg):

        session_id = msg.get('session_id')
        job_id = msg.get('job_id')
        topic = f'inputs/{session_id}/{job_id}'
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
                return replay
    
    def subscribe_drop(self, callback):
        topic = f'executor/{name}/drop'

        def on_message(_client, _userdata, message):
            payload = json.loads(message.payload)
            callback(payload)

        self.client.message_callback_add(topic, on_message)

    def subscribe_execute(self, callback):
        topic = f'executor/{name}/execute'

        def on_message(_client, _userdata, message):
            payload = json.loads(message.payload)
            callback(payload)

        self.client.message_callback_add(topic, on_message)

    def loop(self):
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()
