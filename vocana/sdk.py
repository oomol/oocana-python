from .mainframe import Mainframe

class VocanaSDK:
    __flow_task_id: str
    __node_task_id: str
    __node_id: str
    __props: dict
    __options: dict

    def __init__(self, node_props, mainframe: Mainframe) -> None:
        self.__props = node_props.get('props')
        self.__options = node_props.get('options')
        self.__mainframe = mainframe
        self.__flow_task_id = node_props.get('flow_task_id')
        self.__node_task_id = node_props.get('node_task_id')
        self.__node_id = node_props.get('node_id')

    @property
    def flow_task_id(self):
        return self.__flow_task_id
    
    @property
    def node_task_id(self):
        return self.__node_task_id
    
    @property
    def node_id(self):
        return self.__node_id
    
    @property
    def props(self):
        return self.__props
    
    @property
    def options(self):
        return self.__options

    def result(self, result: any, handle_id: str, done: bool = False):
        node_result = {
            'type': 'NodeResult',
            'flow_task_id': self.__flow_task_id,
            'node_task_id': self.__node_task_id,
            'node_id': self.__node_id,
            'handle_id': handle_id,
            'result': result,
            'done': done,
        }
        self.__mainframe.send(node_result)
        if done:
            self.__mainframe.disconnect()

    def done(self):
        self.__mainframe.send({
            'type': 'NodeDone',
            'flow_task_id': self.__flow_task_id,
            'node_task_id': self.__node_task_id,
            'node_id': self.__node_id,
        })
        self.__mainframe.disconnect()

    def send_error(self, error: str):
        self.__mainframe.send({
            'type': 'NodeError',
            'flow_task_id': self.__flow_task_id,
            'node_task_id': self.__node_task_id,
            'node_id': self.__node_id,
            'error': error,
        })
        self.__mainframe.disconnect()
