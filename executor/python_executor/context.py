import logging
from oocana import Mainframe, Context, StoreKey, BlockInfo, InputHandleDef
from typing import Dict
from .secret import replace_secret
import os.path

logger = logging.getLogger("EXECUTOR_NAME")


def createContext(
    mainframe: Mainframe, session_id: str, job_id: str, store, output, session_dir: str
) -> Context:
    

    node_props = mainframe.notify_block_ready(session_id, job_id)

    inputs_def: Dict[str, Dict] | None = node_props.get("inputs_def")
    inputs = node_props.get("inputs")

    if inputs_def is not None and inputs is not None:

        inputs_def_handles: Dict[str, InputHandleDef] = {}
        for k, v in inputs_def.items():
            inputs_def_handles[k] = InputHandleDef(**v)

        inputs = replace_secret(inputs, inputs_def_handles, node_props.get("inputs_def_patch"))

        for k, v in inputs.items():
            input_def = inputs_def_handles.get(k)
            if input_def is None:
                continue
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
            elif input_def.is_bin_handle():
                if isinstance(v, str):
                    # check file path v is exist
                    if not os.path.exists(v):
                        logger.error(f"file {v} for oomol/bin is not found")
                        continue

                    with open(v, "rb") as f:
                        inputs[k] = f.read()
                else:
                    logger.error(f"not valid bin handle: {v}")

    if inputs is None:
        inputs = {}
    
    blockInfo = BlockInfo(**node_props)

    return Context(inputs, blockInfo, mainframe, store, output, session_dir)