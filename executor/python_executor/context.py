import logging
from oocana import Mainframe, Context, StoreKey, BlockInfo, InputHandleDef
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

        for k, v in inputs.items():
            if inputs_def.get(k) is None:
                continue
            input_def = InputHandleDef(**inputs_def.get(k, {}))
            if input_def.is_var_handle():
                try:
                    ref = StoreKey(**v)
                except:  # noqa: E722
                    logger.warning(f"not valid object ref: {v}")
                    continue
                if ref in store:
                    inputs[k] = store.get(ref)
                else:
                    logger.error(f"object {ref} not found in store")


    if inputs is None:
        inputs = {}
    
    blockInfo = BlockInfo(**node_props)

    return Context(inputs, blockInfo, mainframe, store, output, session_dir)