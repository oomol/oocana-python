from dataclasses import dataclass
from typing import Any, Optional, Literal, TypeAlias, Dict


ContentMediaType: TypeAlias = Literal["oomol/bin", "oomol/secret", "oomol/var"]

@dataclass(frozen=True, kw_only=True)
class JsonSchema:
    """ The JSON schema of the handle. It contains the schema of the handle's content.
        but we only need the contentMediaType to check the handle's type here.
    """

    contentMediaType: Optional[ContentMediaType] = None
    """The media type of the content of the schema."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

@dataclass(frozen=True, kw_only=True)
class HandleDef:
    handle: str
    """The name of the handle. it should be unique in handle list."""

    json_schema: Optional[JsonSchema] = None
    """The schema of the handle. It is used to validate the handle's content."""

    name: Optional[str] = None
    """A alias of the handle's type name. It is used to display in the UI and connect to the other handle match"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
        json_schema = self.json_schema
        if json_schema is not None and not isinstance(json_schema, JsonSchema):
                object.__setattr__(self, "json_schema", JsonSchema(**json_schema))

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

@dataclass(frozen=True, kw_only=True)
class InputHandleDef(HandleDef):
    value: Optional[Any] = None