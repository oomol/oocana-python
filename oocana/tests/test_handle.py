import unittest
from oocana import HandleDef, InputHandleDef, FieldSchema, OutputHandleDef
from typing import cast

missing_handle = {
}

redundant_handle = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/bin"
    },
    "no_used_field": "test"
}

simple_handle = {
    "handle": "test",
}

value_input_handle = {
    "handle": "test",
    "value": "test_value",
}

bin_handle = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/bin"
    },
}

var_handle = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/var"
    },
    "name": "options"
}

secret_handle = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/secret"
    }
}

serializable_var_input_handle = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/var"
    },
    "serialize_for_cache": True
}

serializable_var_output_handle = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/var"
    },
    "__serialize_for_cache": True
}

class TestHandleData(unittest.TestCase):

    def test_error_handle(self):
        """Test that error handle raises ValueError."""
        with self.assertRaises(ValueError, msg="missing attr key: 'handle'"):
            HandleDef(**missing_handle)

    def test_simple_handle(self):
        """Test that simple handle can be created."""
        handle_def = HandleDef(**simple_handle)
        self.assertEqual(handle_def.handle, "test")


        # get attributes
        self.assertEqual(handle_def.get("handle"), "test")
        self.assertEqual(handle_def["handle"], "test")
        self.assertTrue("handle" in handle_def)

        self.assertIsNone(handle_def.description)
        self.assertIsNone(handle_def.json_schema)
        self.assertIsNone(handle_def.kind)
        self.assertIsNone(handle_def.nullable)
        self.assertIsNone(handle_def.is_additional)

        self.assertFalse(handle_def.is_var_handle())
        self.assertFalse(handle_def.is_secret_handle())
        self.assertFalse(handle_def.is_bin_handle())

        # input
        input_def = InputHandleDef(**simple_handle)
        self.assertEqual(input_def.handle, "test")
        self.assertFalse(input_def.is_var_handle())
        self.assertFalse(input_def.is_secret_handle())
        self.assertFalse(input_def.is_bin_handle())
        
        self.assertIsNone(input_def.value)
        self.assertFalse(input_def.has_value())

        # output
        output_def = OutputHandleDef(**simple_handle)
        self.assertEqual(output_def.handle, "test")
        self.assertFalse(output_def.is_var_handle())
        self.assertFalse(output_def.is_secret_handle())
        self.assertFalse(output_def.is_bin_handle())

        self.assertFalse(output_def.need_serialize_var_for_cache())

    def test_redundant_bin_handle(self):
        """Test that redundant fields in handle are ignored."""
        handle_def = HandleDef(**redundant_handle)
        self.assertEqual(handle_def.handle, "test")

        self.assertEqual(handle_def.get("no_used_field"), "test")

    def test_value_input_handle(self):
        """Test that input handle with value can be created."""
        input_def = InputHandleDef(**value_input_handle)
        self.assertEqual(input_def.handle, "test")
        self.assertEqual(input_def.value, "test_value")

        self.assertTrue(input_def.has_value())

    def test_serializable_var_input_handle(self):
        """Test that serializable var input handle can be created."""
        input_def = InputHandleDef(**serializable_var_input_handle)
        self.assertEqual(input_def.handle, "test")
        self.assertTrue(input_def.is_var_handle())
        self.assertTrue(input_def.serialize_for_cache)

    def test_serializable_var_output_handle(self):
        """Test that serializable var output handle can be created."""
        output_def = OutputHandleDef(**serializable_var_output_handle)
        self.assertEqual(output_def.handle, "test")
        self.assertTrue(output_def.is_var_handle())
        self.assertTrue(output_def.need_serialize_var_for_cache())

    def test_secret_handle(self):

        handle_def = HandleDef(**secret_handle)
        self.assertTrue(handle_def.is_secret_handle())


    def test_object_handle(self):
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
        handle_def = HandleDef(**d)
        self.assertFalse(handle_def.is_bin_handle())
        self.assertFalse(handle_def.is_var_handle())
        self.assertFalse(handle_def.is_secret_handle())