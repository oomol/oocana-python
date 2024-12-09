from typing import Literal, Dict, Optional, TypeAlias
from dataclasses import dataclass

OomolType = Literal["oomol/var", "oomol/secret", "oomol/bin"]

ContentMediaType: TypeAlias = Literal["oomol/bin", "oomol/secret", "oomol/var"]

@dataclass(frozen=True, kw_only=True)
class FieldSchema:
    """ The JSON schema of the handle. It contains the schema of the handle's content.
        but we only need the contentMediaType to check the handle's type here.
    """

    contentMediaType: Optional[ContentMediaType] = None
    """The media type of the content of the schema."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    @staticmethod
    def generate_schema(dict: Dict):
        if VarFieldSchema.is_var_dict(dict):
            return VarFieldSchema(**dict)
        elif SecretFieldSchema.is_secret_dict(dict):
            return SecretFieldSchema(**dict)
        elif PrimitiveFieldSchema.is_primitive_dict(dict):
            return PrimitiveFieldSchema(**dict)
        elif ArrayFieldSchema.is_array_dict(dict):
            return ArrayFieldSchema(**dict)
        elif ObjectFieldSchema.is_object_dict(dict):
            return ObjectFieldSchema(**dict)
        else:
            return FieldSchema(**dict)

@dataclass(frozen=True, kw_only=True)
class PrimitiveFieldSchema(FieldSchema):
    type: Literal["string", "number", "boolean"]
    contentMediaType: None = None
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    @staticmethod
    def is_primitive_dict(dict: Dict):
        return dict.get("type") in ["string", "number", "boolean"] and dict.get("contentMediaType") is None

@dataclass(frozen=True, kw_only=True)
class VarFieldSchema(FieldSchema):
    contentMediaType: Literal["oomol/var"] = "oomol/var"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    @staticmethod
    def is_var_dict(dict: Dict):
        return dict.get("contentMediaType") == "oomol/var"

@dataclass(frozen=True, kw_only=True)
class SecretFieldSchema(FieldSchema):
    type: Literal["string"] = "string"
    contentMediaType: Literal["oomol/secret"] = "oomol/secret"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    @staticmethod
    def is_secret_dict(dict: Dict):
        return dict.get("contentMediaType") == "oomol/secret" and dict.get("type") == "string"

@dataclass(frozen=True, kw_only=True)
class ArrayFieldSchema(FieldSchema):
    type: Literal["array"] = "array"
    items: Optional['FieldSchema'] = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
        items = self.items
        if items is not None and not isinstance(items, FieldSchema):
            object.__setattr__(self, "items", FieldSchema.generate_schema(items))

    @staticmethod
    def is_array_dict(dict: Dict):
        return dict.get("type") == "array"

@dataclass(frozen=True, kw_only=True)
class ObjectFieldSchema(FieldSchema):
    type: Literal["object"] = "object"
    properties: Optional[Dict[str, 'FieldSchema']] = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

        properties = self.properties
        if properties is not None:
            for key, value in properties.items():
                if not isinstance(value, FieldSchema):
                    properties[key] = FieldSchema.generate_schema(value)
    
    @staticmethod
    def is_object_dict(dict: Dict):
        return dict.get("type") == "object"
