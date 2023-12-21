from .mainframe import Mainframe

class VocanaSDK:
    __session_id: str
    __task_id: str
    __block_path: str
    __props: dict
    __stacks: any
    __options: dict

    def __init__(self, node_props, mainframe: Mainframe) -> None:
        self.__props = node_props.get('props')
        self.__options = node_props.get('options')
        self.__session_id = node_props.get('session_id')
        self.__task_id = node_props.get('task_id')
        self.__block_path = node_props.get('block_path')
        self.__stacks = node_props.get('stacks')
        self.__mainframe = mainframe

    @property
    def session_id(self):
        return self.__session_id
    
    @property
    def task_id(self):
        return self.__task_id

    @property
    def props(self):
        return self.__props
    
    @property
    def options(self):
        return self.__options

    def result(self, result: any, key: str, done: bool = False):
        node_result = {
            'type': 'BlockResult',
            'session_id': self.__session_id,
            'task_id': self.__task_id,
            'key': key,
            'result': result,
            'done': done,
        }
        self.__mainframe.send(node_result)
        if done:
            self.__mainframe.disconnect()

    def done(self):
        self.__mainframe.send({
            'type': 'BlockDone',
            'session_id': self.__session_id,
            'task_id': self.__task_id,
        })
        self.__mainframe.disconnect()

    def send_message(self, payload):
        self.__mainframe.send_report({
            'type': 'BlockMessage',
            'session_id': self.__session_id,
            'block_task_id': self.__task_id,
            'block_path': self.__block_path,
            'stacks': self.__stacks,
            'payload': payload,
        })

    def log_json(self, payload):
        self.__mainframe.send_report({
            'type': 'BlockLogJSON',
            'session_id': self.__session_id,
            'block_task_id': self.__task_id,
            'block_path': self.__block_path,
            'stacks': self.__stacks,
            'json': payload,
        })

    def send_error(self, error: str):
        self.__mainframe.send({
            'type': 'BlockError',
            'session_id': self.__session_id,
            'task_id': self.__task_id,
            'error': error,
        })
        self.__mainframe.disconnect()
