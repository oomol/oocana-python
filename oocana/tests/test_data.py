import unittest
from oocana import data

class TestData(unittest.TestCase):

    def test_store_key_missing(self):
        store_key_dict = {
            "executor": "executor",
            "handle": "handle",
            "job_id": "job_id",
        }

        with self.assertRaises(ValueError):
            data.StoreKey(**store_key_dict)

    def test_store_key_extra(self):
        store_key_dict = {
            "executor": "executor",
            "handle": "handle",
            "job_id": "job_id",
            "session_id": "session_id",
            "extra": "extra"
        }
        store_key = data.StoreKey(**store_key_dict)
        self.assertEqual(store_key.executor, 'executor')
        self.assertEqual(store_key.handle, 'handle')
        self.assertEqual(store_key.job_id, 'job_id')
        self.assertEqual(store_key.session_id, 'session_id')

    def test_block_info_missing(self):
        block_info_dict = {
            "session_id": "session_id_one",
            "stacks": ["stack1", "stack2"],
        }

        with self.assertRaises(ValueError):
            data.BlockInfo(**block_info_dict)

    def test_block_info_extra(self):
        block_info_dict = {
            "session_id": "session_id_one",
            "job_id": "job_id_one",
            "stacks": ["stack1", "stack2"],
            "block_path": "block_path_one",
            "extra": "extra"
        }

        block_info = data.BlockInfo(**block_info_dict)
        self.assertEqual(block_info.session_id, "session_id_one")
        self.assertEqual(block_info.job_id, "job_id_one")
        self.assertEqual(block_info.stacks, ["stack1", "stack2"])
        self.assertEqual(block_info.block_path, "block_path_one")
