from dataclasses import dataclass
from typing import TypedDict

EXECUTOR_NAME = "python"

class JobDict(TypedDict):
    session_id: str
    job_id: str

class BlockDict(TypedDict):
    session_id: str
    job_id: str
    stacks: list
    block_path: str | None

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
            if key not in kwargs:
                raise ValueError(f"missing key {key}")

    def job_info(self) -> JobDict:
        return {"session_id": self.session_id, "job_id": self.job_id}

    def block_dict(self) -> BlockDict:
        return {
            "session_id": self.session_id,
            "job_id": self.job_id,
            "stacks": self.stacks,
            "block_path": self.block_path,
        }
    

