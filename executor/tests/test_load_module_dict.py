import os
import unittest

from python_executor.block import load_module_dict

# 编写一个继承自 unittest.TestCase 的测试类
class TestLoadModuleDict(unittest.TestCase):

    def test_load_module_from_file(self):
        current_test_file = os.path.abspath(__file__)
        to_run_file_path = os.path.join(os.path.dirname(current_test_file), "test_files", "to_run_file.py")
        module_dict = load_module_dict(
            module_name="to_run_path",
            source=to_run_file_path,
            is_source_path=True,
        )
        func = module_dict.get("main", None)

        if func is None:
            self.assertTrue(False)
            return

        self.assertTrue(callable(func))
        self.assertEqual(func(), 2)
        self.assertEqual(func(), 3)

    def test_load_module_from_source_code(self):
        current_test_file = os.path.abspath(__file__)
        to_run_file_path = os.path.join(os.path.dirname(current_test_file), "test_files", "to_run_file.py")

        with open(to_run_file_path, "r", encoding="utf-8") as file:
            source_code = file.read()

        module_dict= load_module_dict(
            module_name="to_run_source",
            source=source_code,
            is_source_path=False,
        )
        func = module_dict.get("main", None)

        if func is None:
            self.assertTrue(False)
            return

        self.assertTrue(callable(func))
        self.assertEqual(func(), 2)
        self.assertEqual(func(), 3)

# 运行测试
if __name__ == "__main__":
    unittest.main()