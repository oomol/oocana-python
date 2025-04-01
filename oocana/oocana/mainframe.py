from simplejson import loads
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import operator
from urllib.parse import urlparse
import uuid
from .data import BlockDict, JobDict, dumps, EXECUTOR_NAME
import logging
from typing import Optional

__all__ = ["Mainframe"]

class Mainframe:
    address: str
    client: mqtt.Client
    client_id: str
    _subscriptions: set[str] = set()
    _logger: logging.Logger

    def __init__(self, address: str, client_id: Optional[str] = None, logger = None) -> None:
        self.address = address
        self.client_id = client_id or f"python-executor-{uuid.uuid4().hex[:8]}"
        self._logger = logger or logging.getLogger(__name__)

    def connect(self):
        connect_address = (
            self.address
            if operator.contains(self.address, "://")
            else f"mqtt://{self.address}"
        )
        url = urlparse(connect_address)
        client = self._setup_client()
        client.connect(host=url.hostname, port=url.port) # type: ignore
        client.loop_start()
    
    def _setup_client(self):
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
        )
        self.client.logger = self._logger
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect_fail = self.on_connect_fail # type: ignore
        return self.client

    # mqtt v5 重连后，订阅和队列信息会丢失(v3 在初始化时，设置 clean_session 后，会保留两者。
    # 我们的 broker 使用的是 v5，在 on_connect 里订阅，可以保证每次重连都重新订阅上。
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            self._logger.error("connect to broker failed, reason_code: %s", reason_code)
            return
        else:
            self._logger.info("connect to broker success")

        for topic in self._subscriptions.copy(): # 进程冲突
            self._logger.info("resubscribe to topic: {}".format(topic))
            self.client.subscribe(topic, qos=1)

    def on_connect_fail(self) -> None:
        self._logger.error("connect to broker failed")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self._logger.warning("disconnect to broker, reason_code: %s", reason_code)

    # 不等待 publish 完成，使用 qos 参数来会保证消息到达。
    def send(self, job_info: JobDict, msg) -> mqtt.MQTTMessageInfo:
        return self.client.publish(
            f'session/{job_info["session_id"]}', dumps({"job_id": job_info["job_id"], "session_id": job_info["session_id"], **msg}), qos=1
        )

    def report(self, block_info: BlockDict, msg: dict) -> mqtt.MQTTMessageInfo:
        return self.client.publish("report", dumps({**block_info, **msg}), qos=1)
    
    def notify_executor_ready(self, session_id: str, package: str | None, identifier: str | None, debug_port: int | None) -> None:
        self.client.publish(f"session/{session_id}", dumps({
            "type": "ExecutorReady",
            "session_id": session_id,
            "executor_name": EXECUTOR_NAME,
            "package": package,
            "identifier": identifier,
            "debug_port": debug_port,
        }), qos=1)

    def notify_block_ready(self, session_id: str, job_id: str) -> dict:

        topic = f"inputs/{session_id}/{job_id}"
        replay = None

        def on_message_once(_client, _userdata, message):
            nonlocal replay
            self.client.unsubscribe(topic)
            replay = loads(message.payload)

        self.client.subscribe(topic, qos=1)
        self.client.message_callback_add(topic, on_message_once)

        self.client.publish(f"session/{session_id}", dumps({
            "type": "BlockReady",
            "session_id": session_id,
            "job_id": job_id,
        }), qos=1)

        while True:
            if replay is not None:
                self._logger.info("notify ready success in {} {}".format(session_id, job_id))
                return replay
            
    def publish(self, topic, payload):
        self.client.publish(topic, dumps(payload), qos=1)
    
    def subscribe(self, topic: str, callback):
        def on_message(_client, _userdata, message):
            self._logger.info("receive topic: {} payload: {}".format(topic, message.payload))
            payload = loads(message.payload)
            callback(payload)

        self.client.message_callback_add(topic, on_message)
        self._subscriptions.add(topic)

        if self.client.is_connected():
            self.client.subscribe(topic, qos=1)
            self._logger.info("subscribe to topic: {}".format(topic))
        else:
            self._logger.info("wait connected to subscribe to topic: {}".format(topic))


    def unsubscribe(self, topic):
        self.client.message_callback_remove(topic)
        self.client.unsubscribe(topic)
        self._subscriptions.remove(topic)

    def loop(self):
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()
