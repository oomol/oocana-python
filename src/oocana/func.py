from .context import Context
from .mainframe import Mainframe


def createContext(
    mainframe: Mainframe, session_id: str, job_id: str, store, output
) -> Context:

    node_props = mainframe.notify_ready(session_id, job_id)

    return Context(node_props, mainframe, store, output)
