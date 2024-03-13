from .mainframe import Mainframe
from dataclasses import asdict
from .data import RefDescriptor

class VocanaSDK:
    __session_id: str
    __job_id: str
    __props: dict
    __stacks: list[any]
    __block_path: str
    __outputs: any
    __store: any

    def __init__(self, node_props, mainframe: Mainframe, store=None, outputs=None) -> None:
        self.__props = node_props.get('inputs')
        self.__session_id = node_props.get('session_id')
        self.__job_id = node_props.get('job_id')
        self.__stacks = node_props.get('stacks')
        self.__block_path = node_props.get('block_path')

        self.__mainframe = mainframe
        self.__store = store
        self.__outputs = outputs

        if self.__props is None:
            self.__props = {}

        for k, v in self.__props.items():
            if isinstance(v, dict) and v.get('executor') == 'python_executor':
                try:
                    objKey = RefDescriptor(**v)
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
    
    def __store_ref(self, handle: str):
        return RefDescriptor(
            executor="python_executor",
            handle=handle,
            job_id=self.job_id,
            session_id=self.session_id
        )

    def output(self, output: any, handle: str, done: bool = False):

        v = output

        if self.__outputs is not None:
            output_def = self.__outputs.get(handle)
            if output_def is not None and output_def.get('data') and output_def.get('data').get('type') == 'var':
                ref = self.__store_ref(handle)
                print(f'store output {handle} as object ref')
                self.__store[ref] = output
                v = asdict(ref)

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
    
    # 捕获 block 的输出，转发上报到 vocana 中
    def report_log(self, line: str, stdio: str = 'stdout'):
        self.__mainframe.report({
            'type': 'BlockLog',
            'session_id': self.session_id,
            'job_id': self.job_id,
            'block_path': self.__block_path,
            'stacks': self.__stacks,
            'log': line,
            stdio: stdio,
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
