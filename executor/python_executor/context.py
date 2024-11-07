import logging
import json
from oocana import Mainframe, Context, StoreKey, BlockInfo, InputHandleDef
from typing import Any, Dict
import os

logger = logging.getLogger("EXECUTOR_NAME")
SECRET_FILE =  os.path.expanduser("~") + "/app-config/oomol-secrets/secrets.json"

def createContext(
    mainframe: Mainframe, session_id: str, job_id: str, store, output, tmp_dir: str
) -> Context:

    node_props = mainframe.notify_block_ready(session_id, job_id)

    inputs_def: Dict[str, Any] | None = node_props.get("inputs_def") # type: ignore
    inputs = node_props.get("inputs")

    try:
        secretJson = json.load(open(SECRET_FILE))
    except FileNotFoundError:
        logger.warning(f"secret file {SECRET_FILE} not found")
        secretJson = None
    except json.JSONDecodeError:
        logger.error(f"secret file {SECRET_FILE} is not a valid json file")
        secretJson = None

    if inputs_def is not None and inputs is not None:
        for k, v in inputs_def.items():
            input_def = InputHandleDef(**v)
            if input_def.is_var_handle(): # TODO: 即使是 var ，如果传递的是简单类型，也不会存在 store key 上。此时应该不需要 warning
                try:
                    ref = StoreKey(**inputs[k])
                except:  # noqa: E722
                    logger.warn(f"not valid object ref: {inputs[k]}")
                    continue
                if ref in store:
                    inputs[k] = store.get(ref)
                else:
                    logger.error(f"object {ref} not found in store")
            elif input_def.is_secret_handle():
                inputs[k] = replace_secret(inputs[k], secretJson)

    elif inputs is None:
        inputs = {}
    
    blockInfo = BlockInfo(**node_props)

    return Context(inputs, blockInfo, mainframe, store, output, tmp_dir)

def replace_secret(path: str, secretJson: dict | None) -> str:
    if secretJson is None:
        # throw error
        logger.error(f"secret file {SECRET_FILE} not found")
        raise ValueError("secret file not found or invalid json file")

    assert isinstance(secretJson, dict)

    try:
        [secretType, secretName, secretKey] =  path.split(",")
    except ValueError:
        logger.error(f"invalid secret path: {path}")
        return ""
    
    s = secretJson.get(secretName)

    if s is None:
        logger.error(f"secret {secretName} not found in {SECRET_FILE}")
        return ""

    if s.get("secretType") != secretType:
        logger.warning(f"secret type mismatch: {s.get('secretType')} != {secretType}")

    secrets: list[Any] = s.get("secrets")
    if secrets:
        for secret in secrets:
            if secret.get("secretKey") == secretKey:
                return secret.get("value")
    else:
        logger.error(f"secret {secretName} has no value")
        return ""

    logger.error(f"secret {secretKey} not found in {secretName}")
    return ""
