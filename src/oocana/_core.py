from .sdk import OocanaSDK
from .mainframe import Mainframe


def setup_sdk(
    mainframe: Mainframe, session_id: str, job_id: str, store, output
) -> OocanaSDK:

    node_props = mainframe.notify_ready(session_id, job_id)

    return OocanaSDK(node_props, mainframe, store, output)
