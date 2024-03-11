from .mainframe import Mainframe
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ObjectRefDescriptor:
    executor: str
    handle: str
    job_id: str
    session_id: str

class VocanaSDK:
    __session_id: str
    __job_id: str
    __props: dict
    __stacks: list[dict]
    __store: any
    __outputs: any

    def __init__(self, node_props, mainframe: Mainframe, store=None, outputs=None) -> None:
        self.__props = node_props.get('inputs')
        self.__session_id = node_props.get('session_id')
        self.__job_id = node_props.get('job_id')
        self.__stacks = node_props.get('stacks')
        self.__mainframe = mainframe
        self.__store = store
        self.__outputs = outputs

        if self.__props is None:
            self.__props = {}

        for k, v in self.__props.items():
            if isinstance(v, dict) and v.get('executor') == 'python_executor':
                try:
                    objKey = ObjectRefDescriptor(**v)
                except:
                    print(f'not valid object ref: {v}')
                    continue

                value = store.get(objKey)

                if value is None:
                    print(f'ObjectRefDescriptor not found: {v}')
                    continue

                self.__props[k] = value

    @property
    def session_id(self):
        return self.__session_id
    
    @property
    def job_id(self):
        return self.__job_id

    @property
    def props(self):
        return self.__props
    
    def __store_obj(self, handle: str):
        return ObjectRefDescriptor(
            executor="python_executor",
            handle=handle,
            job_id=self.job_id,
            session_id=self.session_id
        )
    
    def outputObj(self, obj: any, handle: str, done: bool = False):

        s = self.__store_obj(handle)
        if self.__store is not None:
            self.__store[s] = obj
        self.output(s.__dict__, handle, done)

    def output(self, output: any, handle: str, done: bool = False):

        v = output

        if self.__outputs is not None:
            output_def = self.__outputs.get(handle)
            if output_def is not None and output_def.get('executor'):
                v = self.__store_obj(handle).__dict__

        node_result = {
            'type': 'BlockOutput',
            'session_id': self.session_id,
            'job_id': self.job_id,
            'handle': handle,
            'output': v,
            'done': done,
        }
        self.__mainframe.send(node_result)
        # if done:
        #     self.__mainframe.disconnect()

    def done(self):
        self.__mainframe.send({
            'type': 'BlockDone',
            'session_id': self.__session_id,
            'job_id': self.__job_id,
        })
        # self.__mainframe.disconnect()

    def send_message(self, payload):
        self.__mainframe.report({
            'type': 'BlockMessage',
            'session_id': self.session_id,
            'block_job_id': self.job_id,
            'stacks': self.__stacks,
            'payload': payload,
        })

    def log_json(self, payload):
        self.__mainframe.report({
            'type': 'BlockLogJSON',
            'session_id': self.session_id,
            'block_job_id': self.job_id,
            'stacks': self.__stacks,
            'json': payload,
        })

    def send_error(self, error: str):
        self.__mainframe.send({
            'type': 'BlockError',
            'session_id': self.session_id,
            'job_id': self.job_id,
            'error': error,
        })
        # self.__mainframe.disconnect()
