from dataclasses import dataclass
from typing import Any, Optional, Literal, TypeAlias, Dict


@dataclass(frozen=True, kw_only=True)
class JsonSchema:
    contentMediaType: Optional[Literal["oomol/bin", "oomol/secret", "oomol/var"]] = None

@dataclass(kw_only=True)
class HandleDef:
    handle: str
    json_schema: Optional[JsonSchema] = None
    name: Optional[str] = None

    def __post_init__(self):
        json_schema = self.json_schema
        if json_schema is not None and not isinstance(json_schema, JsonSchema):
                object.__setattr__(self, "json_schema", JsonSchema(**json_schema))

@dataclass(kw_only=True)
class InputHandleDef(HandleDef):
    value: Optional[Any] = None

InputHandles: TypeAlias = Dict[str, InputHandleDef]
OutputHandles: TypeAlias = Dict[str, HandleDef]