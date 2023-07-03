from .argv import parseArgs
from .mainframe import Mainframe
from .sdk import VocanaSDK

def setup_vocana_sdk():
    args = parseArgs()

    mainframe = Mainframe(args.get('address'))
    mainframe.connect()

    node_props = mainframe.send_ready({
        'type': 'NodeReady',
        'flow_task_id': args.get('flow_task_id'),
        'node_task_id': args.get('node_task_id'),
        'node_id': args.get('node_id'),
    })

    return VocanaSDK(node_props, mainframe)
