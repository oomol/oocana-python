import unittest
from oocana import HandleDef, InputHandleDef, OutputHandleDef
from typing import Any, Optional, TypedDict

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
    "_deserialize_from_cache": True
}

serializable_var_output_handle = {
    "handle": "test",
    "json_schema": {
        "contentMediaType": "oomol/var"
    },
    "_serialize_for_cache": True
}

class HandleTestResult(TypedDict):
    handle: str
    description: Optional[str]
    kind: Optional[str]

    is_additional_handle: Optional[bool]
    is_var_handle: bool
    is_secret_handle: bool
    is_bin_handle: bool

class InputHandleTestResult(HandleTestResult):
    nullable: Optional[bool]
    is_serializable_var: bool
    value: Optional[Any]
    has_value: bool

class OutputHandleTestResult(HandleTestResult):
    need_serialize_var_for_cache: bool

class TestHandleData(unittest.TestCase):

    def handle_test(self, handle_def: HandleDef, expected: HandleTestResult):
        self.assertEqual(handle_def.handle, expected["handle"])
        self.assertEqual(handle_def.description, expected["description"])
        self.assertEqual(handle_def.kind, expected["kind"])
        
        self.assertEqual(handle_def.is_additional_handle(), expected["is_additional_handle"])
        self.assertEqual(handle_def.is_var_handle(), expected["is_var_handle"])
        self.assertEqual(handle_def.is_secret_handle(), expected["is_secret_handle"])
        self.assertEqual(handle_def.is_bin_handle(), expected["is_bin_handle"])

    def input_handle_test(self, input_def: InputHandleDef, expected: InputHandleTestResult):
        self.handle_test(input_def, expected)
        self.assertEqual(input_def.nullable, expected["nullable"])
        self.assertEqual(input_def.is_serializable_var(), expected["is_serializable_var"])
        self.assertEqual(input_def.value, expected["value"])
        self.assertEqual(input_def.has_value(), expected["has_value"])

    def output_handle_test(self, output_def: OutputHandleDef, expected: OutputHandleTestResult):
        self.handle_test(output_def, expected)
        self.assertEqual(output_def.need_serialize_var_for_cache(), expected["need_serialize_var_for_cache"])

    def test_error_handle(self):
        """Test that error handle raises ValueError."""
        with self.assertRaises(ValueError, msg="missing attr key: 'handle'"):
            HandleDef(**missing_handle)

    def test_simple_handle(self):
        """Test that simple handle can be created."""
        handle_def = HandleDef(**simple_handle)

        # get attributes
        self.assertEqual(handle_def.get("handle"), "test")
        self.assertEqual(handle_def["handle"], "test")
        self.assertTrue("handle" in handle_def)

        # test handle
        self.handle_test(handle_def, {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": False
        })

    def test_simple_input_output_handle(self):
        # input
        self.input_handle_test(InputHandleDef(**simple_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "nullable": None,
            "value": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "is_serializable_var": False,
            "has_value": False
        })

    def test_simple_output_handle(self):
        # output
        output_def = OutputHandleDef(**simple_handle)
        self.output_handle_test(output_def, {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "need_serialize_var_for_cache": False
        })

    def test_redundant_handle(self):
        """Test that redundant fields in handle are ignored."""
        handle_def = HandleDef(**redundant_handle)
        self.assertEqual(handle_def.handle, "test")

    def test_value_input_handle(self):
        self.input_handle_test(InputHandleDef(**value_input_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "nullable": None,
            "value": "test_value",
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "is_serializable_var": False,
            "has_value": True
        })

    def test_serializable_var_input_handle(self):
        """Test that serializable var input handle can be created."""
        input_def = InputHandleDef(**serializable_var_input_handle)
        self.input_handle_test(input_def, {
            "handle": "test",
            "description": None,
            "kind": None,
            "nullable": None,
            "value": None,
            "is_additional_handle": False,
            "is_var_handle": True,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "is_serializable_var": True,
            "has_value": False
        })

    def test_serializable_var_output_handle(self):
        """Test that serializable var output handle can be created."""
        output_def = OutputHandleDef(**serializable_var_output_handle)
        self.output_handle_test(output_def, {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": True,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "need_serialize_var_for_cache": True
        })

    def test_json_schema(self):
        """Test that json schema can be converted to dict."""
        d = {
            "handle": "test",
            "json_schema": {
                "type": "object",
                "properties": {
                    "name": { "type": "string" },
                    "age": { "type": "number" }
                },
            }
        }
        handle_def = HandleDef(**d)
        self.assertEqual(handle_def.json_schema_to_dict(), d["json_schema"])
        self.assertIsInstance(d["json_schema"]["properties"]["name"], dict)

    def test_var_handle(self):
        self.handle_test(HandleDef(**var_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": True,
            "is_secret_handle": False,
            "is_bin_handle": False
        })

        self.input_handle_test(InputHandleDef(**var_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "nullable": None,
            "value": None,
            "is_additional_handle": False,
            "is_var_handle": True,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "is_serializable_var": False,
            "has_value": False
        })

        self.output_handle_test(OutputHandleDef(**var_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": True,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "need_serialize_var_for_cache": False
        })

    def test_secret_handle(self):
        self.handle_test(HandleDef(**secret_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": True,
            "is_bin_handle": False
        })

        self.input_handle_test(InputHandleDef(**secret_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "nullable": None,
            "value": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": True,
            "is_bin_handle": False,
            "is_serializable_var": False,
            "has_value": False
        })

        self.output_handle_test(OutputHandleDef(**secret_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": True,
            "is_bin_handle": False,
            "need_serialize_var_for_cache": False
        })

    def test_bin_handle(self):
        self.handle_test(HandleDef(**bin_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": True
        })

        self.input_handle_test(InputHandleDef(**bin_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "nullable": None,
            "value": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": True,
            "is_serializable_var": False,
            "has_value": False
        })

        self.output_handle_test(OutputHandleDef(**bin_handle), {
            "handle": "test",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": True,
            "need_serialize_var_for_cache": False
        })


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
        self.handle_test(HandleDef(**d), {
            "handle": "auto_slices",
            "description": None,           
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": False
        })

        self.input_handle_test(InputHandleDef(**d), {
            "handle": "auto_slices",
            "description": None,
            "kind": None,
            "nullable": None,
            "value": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "is_serializable_var": False,
            "has_value": False
        })

        self.output_handle_test(OutputHandleDef(**d), {
            "handle": "auto_slices",
            "description": None,
            "kind": None,
            "is_additional_handle": False,
            "is_var_handle": False,
            "is_secret_handle": False,
            "is_bin_handle": False,
            "need_serialize_var_for_cache": False
        })