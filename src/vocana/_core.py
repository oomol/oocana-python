from .sdk import VocanaSDK
from .mainframe import Mainframe


def setup_vocana_sdk(mainframe: Mainframe, session_id: str, job_id: str) -> VocanaSDK:
    # FIXME: remove this after vocana-rust supports timeout

    node_props = mainframe.notify_ready({
        'type': 'BlockReady',
        'session_id': session_id,
        'job_id': job_id,
    })

    return VocanaSDK(node_props, mainframe)
