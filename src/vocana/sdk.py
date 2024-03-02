from .mainframe import Mainframe

class VocanaSDK:
    __session_id: str
    __job_id: str
    __props: dict
    __stacks: list[dict]

    def __init__(self, node_props, mainframe: Mainframe) -> None:
        self.__props = node_props.get('props')
        self.__session_id = node_props.get('session_id')
        self.__job_id = node_props.get('job_id')
        self.__stacks = node_props.get('stacks')
        self.__mainframe = mainframe

    @property
    def session_id(self):
        return self.__session_id
    
    @property
    def job_id(self):
        return self.__job_id

    @property
    def props(self):
        return self.__props
    
    def outputObj(self, obj: any, handle: str, done: bool = False):
        node_result = {
            'type': 'BlockOutput',
            'session_id': self.session_id,
            'job_id': self.job_id,
            'handle': handle,
            'output': obj,
            'done': done,
        }
        self.__mainframe.send(node_result)

    def output(self, output: any, handle: str, done: bool = False):
        node_result = {
            'type': 'BlockOutput',
            'session_id': self.session_id,
            'job_id': self.job_id,
            'handle': handle,
            'output': output,
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
