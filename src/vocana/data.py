from dataclasses import dataclass

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