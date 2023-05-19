from .mainframe import Mainframe

class VocanaSDK:
    __graph_task_id: str
    __node_task_id: str
    __node_id: str
    __props: dict
    __options: dict

    def __init__(self, props: dict, mainframe: Mainframe) -> None:
        self.__props = props
        self.__mainframe = mainframe
        self.__graph_task_id = props.get('graph_task_id')
        self.__node_task_id = props.get('node_task_id')
        self.__node_id = props.get('node_id')

    @property
    def graph_task_id(self):
        return self.__graph_task_id
    
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
        self.__mainframe.send({
            'type': 'NodeResult',
            'graph_task_id': self.__graph_task_id,
            'node_task_id': self.__node_task_id,
            'node_id': self.__node_id,
            'handle_id': handle_id,
            'result': result,
            'done': done,
        })

        if done:
            self.__mainframe.disconnect()

    def done(self):
        self.__mainframe.send({
            'type': 'NodeDone',
            'graph_task_id': self.__graph_task_id,
            'node_task_id': self.__node_task_id,
            'node_id': self.__node_id,
        })
        self.__mainframe.disconnect()
