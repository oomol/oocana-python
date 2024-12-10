import unittest
from oocana import FieldSchema, is_secret_dict, SecretFieldSchema, is_var_dict, VarFieldSchema, is_array_dict, ArrayFieldSchema, is_object_dict, ObjectFieldSchema
from typing import cast

secret_fixture = {
    "type": "string",
    "contentMediaType": "oomol/secret"
}

var_fixture = {
    "contentMediaType": "oomol/var"
}

array_fixture = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

array_secret_fixture = {
    "type": "array",
    "items": {
        "type": "string",
        "contentMediaType": "oomol/secret"
    }
}

object_fixture = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        }
    }
}

object_secret_fixture = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
        },
        "password": {
            "type": "string",
            "contentMediaType": "oomol/secret"
        }
    }
}

class TestSchema(unittest.TestCase):
    def test_secret_field_schema(self):
        self.assertTrue(is_secret_dict(secret_fixture))
        secret = FieldSchema.generate_schema(secret_fixture)
        self.assertIsInstance(secret, SecretFieldSchema)

    def test_var_field_schema(self):
        self.assertTrue(is_var_dict(var_fixture))
        var = FieldSchema.generate_schema(var_fixture)
        self.assertIsInstance(var, VarFieldSchema)
    
    def test_array_field_schema(self):
        self.assertTrue(is_array_dict(array_fixture))
        array = FieldSchema.generate_schema(array_fixture)
        self.assertIsInstance(array, ArrayFieldSchema)

    def test_object_field_schema(self):
        self.assertTrue(is_object_dict(object_fixture))
        obj = FieldSchema.generate_schema(object_fixture)
        self.assertIsInstance(obj, ObjectFieldSchema)

    def test_array_secret_field_schema(self):
        self.assertTrue(is_array_dict(array_secret_fixture))
        array_secret = FieldSchema.generate_schema(array_secret_fixture)
        self.assertIsInstance(array_secret, ArrayFieldSchema)

        array_secret = cast(ArrayFieldSchema, array_secret)
        self.assertIsInstance(array_secret.items, SecretFieldSchema)

    def test_object_secret_field_schema(self):
        self.assertTrue(is_object_dict(object_secret_fixture))
        obj_secret = FieldSchema.generate_schema(object_secret_fixture)
        self.assertIsInstance(obj_secret, ObjectFieldSchema)

        obj_secret = cast(ObjectFieldSchema, obj_secret)
        self.assertIsNotNone(obj_secret.properties)

        if obj_secret.properties is not None:
            self.assertIsInstance(obj_secret.properties["password"], SecretFieldSchema)
        else:
            self.fail("properties is None")