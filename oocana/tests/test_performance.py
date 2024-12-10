import unittest
import timeit
from oocana import handle_data  # 假设 handle_data 包含 HandleDef dataclass


class TestPerformance(unittest.TestCase):
    # 定义一个小的测试函数，用于生成和初始化 HandleDef 实例
    def test_handle_def_creation(self):
        d = {
            "handle": "test",
            "json_schema": {
                "contentMediaType": "oomol/bin"
            },
        }
        handle_def = handle_data.HandleDef(**d)
        assert(handle_def.handle == "test")


if __name__ == "__main__":
    # 使用 timeit 模块测量执行时间
    execution_time = timeit.timeit("test_handle_def_creation()", globals=globals(), number=10000)
    print(f"HandleDef creation and initialization took {execution_time} seconds for 10000 iterations")