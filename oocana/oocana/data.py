from dataclasses import dataclass, asdict
from typing import TypedDict, Any, Optional, Literal, TypeAlias

class JobDict(TypedDict):
    session_id: str
    job_id: str

class BlockDict(TypedDict):
    session_id: str
    job_id: str
    stacks: list
    block_path: str

media_type: TypeAlias = Literal["oomol/bin", "oomol/secret", "oomol/var"]
class JsonSchemaDict(TypedDict):
    contentMediaType: media_type

class HandleDict(TypedDict):
    handle: str
    json_schema: Optional[dict]
    name: Optional[str]

class InputHandleDict(HandleDict):
    value: Any

def is_var_handle(obj) -> bool:

    return check_handle_type(obj, "oomol/var")

def is_secret_handle(obj) -> bool:
    return check_handle_type(obj, "oomol/secret")


def check_handle_type(obj, type: media_type) -> bool:
    if obj.get("handle") is None:
        return False

    if obj.get("json_schema") is None or isinstance(obj.get("json_schema"), dict) is False:
        return False

    if obj.get("json_schema").get("contentMediaType") is None:
        return False
    
    return obj.get("json_schema").get("contentMediaType") == type

# 为了让 dataclass 字段必须一一匹配，如果多一个或者少一个字段，就会报错。这里想兼容额外多余字段，所以需要自己重写 __init__ 方法，忽略处理多余字段。同时需要自己处理缺少字段的情况。
# 因为这样就已经使用了 object.__setattr__ 就可以干脆加上 frozen=True，防止修改。
@dataclass(frozen=True, kw_only=True)
class StoreKey:
    executor: str
    handle: str
    job_id: str
    session_id: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
        for key in self.__annotations__.keys():
            if key not in kwargs:
                raise ValueError(f"missing key {key}")


# 发送 reporter 时，固定需要的 block 信息参数
@dataclass(frozen=True, kw_only=True)
class BlockInfo:

    session_id: str
    job_id: str
    stacks: list
    block_path: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
        for key in self.__annotations__.keys():
            if key not in kwargs:
                raise ValueError(f"missing key {key}")

    def dict(self):
        return asdict(self)

    def job_info(self) -> JobDict:
        return {"session_id": self.session_id, "job_id": self.job_id}

    def block_dict(self) -> BlockDict:
        return {
            "session_id": self.session_id,
            "job_id": self.job_id,
            "stacks": self.stacks,
            "block_path": self.block_path,
        }
    

