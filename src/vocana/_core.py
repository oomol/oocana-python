from .argv import parseArgs
from .mainframe import Mainframe
from .sdk import VocanaSDK
import signal

def timeout_handler(signum, frame):
    raise TimeoutError('setup timeout')

def setup_vocana_sdk(mainframe, session_id, job_id):
    # FIXME: remove this after vocana-rust supports timeout
    timeout_sec = 20000

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_sec)
    try:
        sdk = _setup_vocana_sdk(mainframe, session_id, job_id)
    finally:
        signal.alarm(0)
    return sdk

def _setup_vocana_sdk(mainframe, session_id, job_id):

    node_props = mainframe.send_ready({
        'type': 'BlockReady',
        'session_id': session_id,
        'job_id': job_id,
    })

    return VocanaSDK(node_props, mainframe)
