from dataclasses import dataclass
from typing import Any, Optional
from .schema import FieldSchema, ContentMediaType

__all__ = ["HandleDef", "InputHandleDef"]

@dataclass(frozen=True, kw_only=True)
class HandleDef:
    """The base handle for output def, can be directly used for output def 
    """
    handle: str
    """The name of the handle. it should be unique in handle list."""

    json_schema: Optional[FieldSchema] = None
    """The schema of the handle. It is used to validate the handle's content."""

    name: Optional[str] = None
    """A alias of the handle's type name. It is used to display in the UI and connect to the other handle match"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
        if "handle" not in kwargs:
            raise ValueError("missing attr key: 'handle'")
        json_schema = self.json_schema
        if json_schema is not None and not isinstance(json_schema, FieldSchema):
            object.__setattr__(self, "json_schema", FieldSchema.generate_schema(json_schema))

    def check_handle_type(self, type: ContentMediaType) -> bool:
        if self.handle is None:
            return False
        if self.json_schema is None:
            return False
        if self.json_schema.contentMediaType is None:
            return False
        return self.json_schema.contentMediaType == type

    def is_var_handle(self) -> bool:
        return self.check_handle_type("oomol/var")
    
    def is_secret_handle(self) -> bool:
        return self.check_handle_type("oomol/secret")

    def is_bin_handle(self) -> bool:
        return self.check_handle_type("oomol/bin")

@dataclass(frozen=True, kw_only=True)
class InputHandleDef(HandleDef):

    value: Optional[Any] = None
    """default value for input handle, can be None.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)