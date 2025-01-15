from typing import Literal, Dict, Optional, TypeAlias, Any, cast
from dataclasses import dataclass
from .data import BinValueDict, VarValueDict

__all__ = ["FieldSchema", "PrimitiveFieldSchema", "VarFieldSchema", "SecretFieldSchema", "ArrayFieldSchema", "ObjectFieldSchema", "ContentMediaType", "is_bin_value", "is_var_value", "is_array_dict", "is_object_dict", "is_var_dict", "is_primitive_dict", "is_secret_dict"]

OomolType = Literal["oomol/var", "oomol/secret", "oomol/bin"]

ContentMediaType: TypeAlias = Literal["oomol/bin", "oomol/secret", "oomol/var"]

def is_bin_value(d: BinValueDict | Any):
    if isinstance(d, dict) is False:
        return False
    dd = cast(BinValueDict, d)
    return dd.get("__OOMOL_TYPE__") == "oomol/bin" and isinstance(dd.get("value") , str) 

def is_var_value(d: VarValueDict | Any):
    if isinstance(d, dict) is False:
        return False
    dd = cast(VarValueDict, d)
    return dd.get("__OOMOL_TYPE__") == "oomol/var" and isinstance(dd.get("value") , dict)

def is_array_dict(dict: Dict):
    return dict.get("type") == "array"

def is_object_dict(dict: Dict):
    return dict.get("type") == "object"

def is_var_dict(dict: Dict):
    return dict.get("contentMediaType") == "oomol/var"

def is_primitive_dict(dict: Dict):
    return dict.get("type") in ["string", "number", "boolean"] and dict.get("contentMediaType") is None

def is_secret_dict(dict: Dict):
    return dict.get("contentMediaType") == "oomol/secret" and dict.get("type") == "string"

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
        if is_var_dict(dict):
            return VarFieldSchema(**dict)
        elif is_secret_dict(dict):
            return SecretFieldSchema(**dict)
        elif is_primitive_dict(dict):
            return PrimitiveFieldSchema(**dict)
        elif is_array_dict(dict):
            return ArrayFieldSchema(**dict)
        elif is_object_dict(dict):
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


@dataclass(frozen=True, kw_only=True)
class VarFieldSchema(FieldSchema):
    contentMediaType: Literal["oomol/var"] = "oomol/var"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

@dataclass(frozen=True, kw_only=True)
class SecretFieldSchema(FieldSchema):
    type: Literal["string"] = "string"
    contentMediaType: Literal["oomol/secret"] = "oomol/secret"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

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

