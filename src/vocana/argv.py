import argparse
from typing import TypedDict

Args = TypedDict('Args', {
    'address': str,
    'session_id': str,
    'task_id': str,
})

def parseArgs() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, required=True)
    parser.add_argument('--session-id', type=str, required=True)
    parser.add_argument('--task-id', type=str, required=True)

    args, _ = parser.parse_known_args()
    return Args(args.__dict__)
