import unittest
from oocana import handle_data
from typing import cast


fixture = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/bin"
    },
    "name": "options"
}

class TestHandleData(unittest.TestCase):
    def test_handle_def_field(self):

        d = fixture.copy()
        handle_data.HandleDef(**d)

        d = fixture.copy()
        del d["name"]

        handle_def = handle_data.HandleDef(**d)
        self.assertEqual(handle_def.handle, "test")
        self.assertIsNotNone(handle_def.json_schema)
        
        json_schema = cast(handle_data.FieldSchema, handle_def.json_schema)
        self.assertEqual(json_schema.contentMediaType, "oomol/bin")

        d = fixture.copy()
        del d["name"]
        del d["json_schema"]

        handle_def = handle_data.HandleDef(**d)
        self.assertEqual(handle_def.handle, "test")
        self.assertIsNone(handle_def.json_schema)

    def test_handle_def_extra_field(self):
        d = fixture.copy()
        d["a"] = "a"

        handle_def = handle_data.HandleDef(**d)
        self.assertEqual(handle_def.handle, "test")

    def test_handle_def_missing_field(self):
        d = {
            "a": "1",
        }

        with self.assertRaises(ValueError, msg="missing attr key: 'handle'"):
            handle_data.InputHandleDef(**d) # type: ignore

    def test_handle_type(self):
        d = fixture.copy()
        d["json_schema"]["contentMediaType"] = "oomol/secret"

        handle_def = handle_data.HandleDef(**d)
        self.assertTrue(handle_def.is_secret_handle())

        d["json_schema"]["contentMediaType"] = "oomol/var"
        handle_def = handle_data.HandleDef(**d)
        self.assertTrue(handle_def.is_var_handle())

        d = {
            "handle": "auto_slices",
            "json_schema": {
                "items": {
                    "properties": {
                        "begin": { "type": "number" },
                        "end": { "type": "number" }
                    },
                    "required": ["begin", "end"],
                    "type": "object"
                },
                "type": "array"
            }
        }
        handle_def = handle_data.HandleDef(**d)
        self.assertFalse(handle_def.is_var_handle())
        self.assertFalse(handle_def.is_secret_handle())

    def test_input_handle_type(self):
        d = fixture.copy()
        d["json_schema"]["contentMediaType"] = "oomol/secret"

        handle_def = handle_data.InputHandleDef(**d)
        self.assertTrue(handle_def.is_secret_handle())

        d["json_schema"]["contentMediaType"] = "oomol/var"
        handle_def = handle_data.InputHandleDef(**d)
        self.assertTrue(handle_def.is_var_handle())

        d = {
            "handle": "auto_slices",
            "json_schema": {
                "items": {
                    "properties": {
                        "begin": { "type": "number" },
                        "end": { "type": "number" }
                    },
                    "required": ["begin", "end"],
                    "type": "object"
                    },
                "type": "array"
            }
        }
        handle_def = handle_data.InputHandleDef(**d)
        self.assertFalse(handle_def.is_var_handle())
        self.assertFalse(handle_def.is_secret_handle())