from typing import Any, Dict
from oocana import InputHandleDef, FieldSchema, ObjectFieldSchema, ArrayFieldSchema, SecretFieldSchema
import logging
import os
import json
import re
from .data import EXECUTOR_NAME

logger = logging.getLogger(EXECUTOR_NAME)
SECRET_FILE =  os.path.expanduser("~") + "/app-config/oomol-secrets/secrets.json"

# "${{OO_SECRET:type,name,key}}"，捕获组为 (type,name,key)
SECRET_REGEX = r"\"\$\{\{OO_SECRET:([\S]+),([\S]+),([\S]+)\}\}\""

def replace_secret(
    value: Any,
    root_def: Dict[str, InputHandleDef],
    patch: Dict[str, Any] | None = None,
) -> Any:
    if not isinstance(value, dict):
        return value
    
    try:
        secretJson = json.load(open(SECRET_FILE))
    except FileNotFoundError:
        logger.warning(f"secret file {SECRET_FILE} not found")
        secretJson = None
    except json.JSONDecodeError:
        logger.error(f"secret file {SECRET_FILE} is not a valid json file")
        secretJson = None

    string_value = json.dumps(value)
    result = re.findall(SECRET_REGEX, string_value, re.MULTILINE)
    if result:
        if secretJson is None:
            logger.error(f"secret file {SECRET_FILE} not found")
        else:
            for r in result:
                secret = get_secret(f"{r[0]},{r[1]},{r[2]}", secretJson).replace('"', '\\"')
                string_value = string_value.replace(f"${{{{OO_SECRET:{r[0]},{r[1]},{r[2]}}}}}", secret)
        value = json.loads(string_value)
    
    for k, v in value.items():
        input_def = root_def.get(k)
        if input_def is None:
            continue
        # 如果是 None 就不替换，直接透传。只有 nullable 的情况下才会出现 None
        if input_def.is_secret_handle() and v is not None:
            value[k] = get_secret(v, secretJson)
        # 为了保持功能聚焦，var 部分在 Context 那边重新迭代处理。var 只在根目录，同时重复迭代开销不大。如果要递归，还是要合并进来。
        elif isinstance(input_def.json_schema, ObjectFieldSchema) or isinstance(input_def.json_schema, ArrayFieldSchema):
            replace_sub_secret(v, input_def.json_schema, secretJson)

    if patch is not None:
        patch_def = patch # 避免下面的类型提示错误
        for k, v in patch_def.items():
            input_value = value.get(k)
            if input_value is not None:
                for patch in v:
                    is_secret = patch_def.get("schema", {}).get("contentMediaType") == "oomol/secret"
                    if not is_secret:
                        continue
                    
                    path = patch_def.get("path")
                    if path is None:
                        # 整个替换，所以得是 value 而不是 input_value
                        value[k] = get_secret(input_value, secretJson)
                    elif isinstance(path, str) and path in input_value:
                        input_value[path] = get_secret(input_value[path], secretJson)
                    elif isinstance(path, int) and path < len(input_value):
                        input_value[path] = get_secret(input_value[path], secretJson)
                    elif isinstance(path, list):
                        tmp = input_value
                        for p in path[:-1]:
                            tmp = tmp[p]
                            if tmp is None:
                                logger.error(f"invalid path: {path}")
                                break
                        if tmp is not None:
                            tmp[path[-1]] = get_secret(tmp[path[-1]], secretJson)
                    else:
                        logger.error(f"invalid path: {path}")
            
    return value

def replace_sub_secret(value: Any, field: FieldSchema, secretJson: Dict[str, Any] | None) -> Any:
    if isinstance(value, dict) and isinstance(field, ObjectFieldSchema):
        if field.properties is None:
            return value

        for k, v in value.items():
            schema = field.properties.get(k)
            if schema is None:
                continue
            if isinstance(schema, SecretFieldSchema):
                value[k] = get_secret(v, secretJson)
            elif isinstance(schema, ObjectFieldSchema) or isinstance(schema, ArrayFieldSchema):
                value[k] = replace_sub_secret(v, schema, secretJson)
    elif isinstance(value, list) and isinstance(field, ArrayFieldSchema):
        if field.items is None:
            return value
        
        for i, v in enumerate(value):
            schema = field.items
            if isinstance(schema, SecretFieldSchema):
                value[i] = get_secret(v, secretJson)
            elif isinstance(schema, ObjectFieldSchema) or isinstance(schema, ArrayFieldSchema):
                value[i] = replace_sub_secret(v, schema, secretJson)
            
    return value


def get_secret(path: str, secretJson: dict | None) -> str:
    if secretJson is None:
        # throw error
        logger.error(f"secret file {SECRET_FILE} not found")
        raise ValueError("secret file not found or invalid json file")

    assert isinstance(secretJson, dict)

    try:
        [secretType, secretName, secretKey] =  path.split(",")
    except ValueError:
        logger.error(f"invalid secret path: {path}")
        return path
    
    s = secretJson.get(secretName)

    if s is None:
        logger.error(f"secret {secretName} not found in {SECRET_FILE}")
        return path

    if s.get("secretType") != secretType:
        logger.warning(f"secret type mismatch: {s.get('secretType')} != {secretType}")

    secrets: list[Any] = s.get("secrets")
    if secrets:
        for secret in secrets:
            if secret.get("secretKey") == secretKey:
                return secret.get("value")
    else:
        logger.error(f"secret {secretName} has no value")
        return path

    logger.error(f"secret {secretKey} not found in {secretName}")
    return path
