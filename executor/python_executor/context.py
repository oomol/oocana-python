import logging
from oocana import Mainframe, Context, StoreKey, BlockInfo
from typing import Any, Dict
from .secret import replace_secret

logger = logging.getLogger("EXECUTOR_NAME")


def createContext(
    mainframe: Mainframe, session_id: str, job_id: str, store, output, session_dir: str
) -> Context:

    node_props = mainframe.notify_block_ready(session_id, job_id)

    inputs_def: Dict[str, Any] | None = node_props.get("inputs_def")
    inputs = node_props.get("inputs")

    if inputs_def is not None and inputs is not None:
        inputs = replace_secret(inputs, inputs_def, node_props.get("inputs_def_patch"))

    if inputs is None:
        inputs = {}

    
    
    blockInfo = BlockInfo(**node_props)

    return Context(inputs, blockInfo, mainframe, store, output, session_dir)