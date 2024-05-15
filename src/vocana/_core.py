from .sdk import VocanaSDK
from .mainframe import Mainframe


def setup_vocana_sdk(
    mainframe: Mainframe, session_id: str, job_id: str, store, output
) -> VocanaSDK:

    node_props = mainframe.notify_ready(session_id, job_id)

    return VocanaSDK(node_props, mainframe, store, output)
