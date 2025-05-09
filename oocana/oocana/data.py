from dataclasses import dataclass, asdict
from typing import TypedDict, Literal
from simplejson import JSONEncoder
import simplejson as json

EXECUTOR_NAME = "python"

__all__ = ["dumps", "BinValueDict", "VarValueDict", "JobDict", "BlockDict", "StoreKey", "BlockInfo", "EXECUTOR_NAME", "JobDict", "BinValueDict", "VarValueDict"]

def dumps(obj, **kwargs):
    return json.dumps(obj, cls=DataclassJSONEncoder, ignore_nan=True, **kwargs)

class DataclassJSONEncoder(JSONEncoder):
    def default(self, o): # pyright: ignore[reportIncompatibleMethodOverride]
        if hasattr(o, '__dataclass_fields__'):
            return asdict(o)
        return JSONEncoder.default(self, o)

class BinValueDict(TypedDict):
    value: str
    __OOMOL_TYPE__: Literal["oomol/bin"]

class VarValueDict(TypedDict):
    value: dict
    __OOMOL_TYPE__: Literal["oomol/var"]

class JobDict(TypedDict):
    session_id: str
    job_id: str

class BlockDict(TypedDict):
    session_id: str
    job_id: str
    stacks: list
    block_path: str | None # better to use NotRequired here, but it is not supported in python 3.10 and type_extensions requires high version, For compatibility, use None instead of NotRequired.

# dataclass 默认字段必须一一匹配
# 如果多一个或者少一个字段，就会报错。
# 这里想兼容额外多余字段，所以需要自己重写 __init__ 方法，忽略处理多余字段。同时需要自己处理缺少字段的情况。
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
    block_path: str | None = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
        for key in self.__annotations__.keys():
            if key not in kwargs and key != "block_path":
                raise ValueError(f"missing key {key}")

    def job_info(self) -> JobDict:
        return {"session_id": self.session_id, "job_id": self.job_id}

    def block_dict(self) -> BlockDict:
        if self.block_path is None:
            return {
                "session_id": self.session_id,
                "job_id": self.job_id,
                "stacks": self.stacks,
            } # type: ignore[return-value]

        return {
            "session_id": self.session_id,
            "job_id": self.job_id,
            "stacks": self.stacks,
            "block_path": self.block_path,
        }
    

