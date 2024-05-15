import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import operator
from urllib.parse import urlparse
import uuid
from .data import BlockDict, JobDict
import logging

name = "python_executor"

logger = logging.getLogger(__name__)

class Mainframe:
    address: str
    client: mqtt.Client

    def __init__(self, address: str) -> None:
        self.address = address

    def is_connected(self):
        return self.client is not None and self.client.is_connected()

    def connect(self):
        connect_address = (
            self.address
            if operator.contains(self.address, "://")
            else f"mqtt://{self.address}"
        )
        url = urlparse(connect_address)

        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=f"python-executor-{uuid.uuid4().hex[:8]}"
        )
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect_fail = self.on_connect_fail # type: ignore
        self.client.connect(host=url.hostname, port=url.port) # type: ignore
        self.client.loop_start()
        return self.client

    # mqtt v5 重连后，订阅和队列信息会丢失(v3 在初始化时，设置 clean_session 后，会保留两者。
    # 我们的 broker 使用的是 v5，在 on_connect 里订阅，可以保证每次重连都重新订阅上。
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            logger.error("connect to broker failed, reason_code: %s", reason_code)
            return
        else:
            logger.info("connect to broker success")

        client.subscribe(f"executor/{name}/execute", qos=1)
        client.subscribe(f"executor/{name}/drop", qos=1)

    def on_connect_fail(self) -> None:
        logger.error("connect to broker failed")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        logger.warning("disconnect to broker, reason_code: %s", reason_code)

    def send(self, job_info: JobDict, msg):
        if self.is_connected() is False:
            logger.error("SDK is not ready when send message {} {}".format(job_info, msg))
            raise Exception("SDK is not ready when send message")

        info = self.client.publish(
            f'session/{job_info["session_id"]}', json.dumps({"job_id": job_info["job_id"], "session_id": job_info["session_id"], **msg}), qos=1
        )
        info.wait_for_publish()

    def report(self, block_info: BlockDict, msg: dict):
        if self.is_connected() is False:
            logger.error("SDK is not ready when report message {} {}".format(block_info, msg))
            raise Exception("SDK is not ready when report message")
        info = self.client.publish("report", json.dumps({**block_info, **msg}), qos=1)
        info.wait_for_publish()

    def notify_ready(self, msg):

        session_id = msg.get("session_id")
        job_id = msg.get("job_id")
        topic = f"inputs/{session_id}/{job_id}"
        replay = None

        def on_message_once(_client, _userdata, message):
            nonlocal replay
            self.client.unsubscribe(topic)
            replay = json.loads(message.payload)

        self.client.subscribe(topic, qos=1)
        self.client.message_callback_add(topic, on_message_once)

        self.client.publish(f"session/{session_id}", json.dumps(msg), qos=1)

        while True:
            if replay is not None:
                logger.info("notify ready success in {} {}".format(session_id, job_id))
                return replay

    def subscribe_drop(self, callback):
        topic = f"executor/{name}/drop"

        def on_message(_client, _userdata, message):
            logger.info("drop message: {}".format(message.payload))
            payload = json.loads(message.payload)
            callback(payload)

        self.client.message_callback_add(topic, on_message)

    def subscribe_execute(self, callback):
        topic = f"executor/{name}/execute"

        def on_message(_client, _userdata, message):
            logger.info("execute message: {}".format(message.payload))
            payload = json.loads(message.payload)
            callback(payload)

        self.client.message_callback_add(topic, on_message)

    def loop(self):
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()
