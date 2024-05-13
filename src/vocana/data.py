from dataclasses import dataclass
from typing import TypedDict

class JobDict(TypedDict):
    session_id: str
    job_id: str

class BlockDict(TypedDict):
    session_id: str
    job_id: str
    stacks: list
    block_path: str

# 默认的 dataclass 字段必须一一匹配，如果多一个或者少一个字段，就会报错。
# 这里在使用 frozen 固化数据的同时，做了多余字段的忽略处理。如果不 frozen 的话，不需要使用 object.__setattr__ 这种方式来赋值，这种方式会有一点性能开销。


@dataclass(frozen=True, init=False)
class RefDescriptor:
    executor: str
    handle: str
    job_id: str
    session_id: str

    def __init__(self, *args, **kwargs):
        if args:
            object.__setattr__(self, "executor", args[0])
            object.__setattr__(self, "handle", args[1])
            object.__setattr__(self, "job_id", args[2])
            object.__setattr__(self, "session_id", args[3])
        if kwargs:
            for key, value in kwargs.items():
                object.__setattr__(self, key, value)


# 发送 reporter 时，固定需要的 block 信息参数
@dataclass(frozen=True)
class BlockInfo:

    # 以下四个参数，在发送数据时，都需要传递过去。
    session_id: str
    job_id: str
    stacks: list
    block_path: str

    def __init__(self, *args, **kwargs):
        if args:
            object.__setattr__(self, "session_id", args[0])
            object.__setattr__(self, "job_id", args[1])
            object.__setattr__(self, "stacks", args[2])
            object.__setattr__(self, "block_path", args[3])
        if kwargs:
            for key, value in kwargs.items():
                object.__setattr__(self, key, value)

    def dict(self):
        return {
            "session_id": self.session_id,
            "job_id": self.job_id,
            "stacks": self.stacks,
            "block_path": self.block_path,
        }

    def job_info(self) -> JobDict:
        return {"session_id": self.session_id, "job_id": self.job_id}

    def block_dict(self) -> BlockDict:
        return {
            "session_id": self.session_id,
            "job_id": self.job_id,
            "stacks": self.stacks,
            "block_path": self.block_path,
        }