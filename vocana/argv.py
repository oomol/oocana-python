import argparse
from typing import TypedDict

Args = TypedDict('Args', {
    'address': str,
    'graph_task_id': str,
    'node_task_id': str,
    'node_id': str,
})

def parseArgs() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, required=True)
    parser.add_argument('--graph-task-id', type=str, required=True)
    parser.add_argument('--node-task-id', type=str, required=True)
    parser.add_argument('--node-id', type=str, required=True)

    args = parser.parse_args()
    return Args(args.__dict__)
