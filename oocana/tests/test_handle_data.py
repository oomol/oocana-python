import unittest
from oocana import handle_data
from typing import cast

class TestHandleData(unittest.TestCase):
    def test_handle_def_option_field(self):
        d = {
            "handle": "test",
            "json_schema": {
                "contentMediaType": "oomol/bin"
            },
        }

        handle_def = handle_data.HandleDef(**d)
        self.assertEqual(handle_def.handle, "test")
        self.assertIsNotNone(handle_def.json_schema)
        
        json_schema = cast(handle_data.JsonSchema, handle_def.json_schema)
        self.assertEqual(json_schema.contentMediaType, "oomol/bin")

    def test_input_handle_def_option_field(self):

        d = {
            "handle": "test",
        }

        handle_def = handle_data.HandleDef(**d) # type: ignore
        self.assertEqual(handle_def.handle, "test")
        self.assertIsNone(handle_def.json_schema)

    