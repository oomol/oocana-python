
from typing import Any, TypedDict, List, Literal, TypeAlias, Union

class TablePreviewData(TypedDict):
    columns: List[str | int | float]
    rows: List[List[str | int | float | bool]]
    row_count: int | None

class TablePreviewPayload(TypedDict):
    type: Literal['table']
    data: TablePreviewData | Any

class TextPreviewPayload(TypedDict):
    type: Literal["text"]
    data: Any

class JSONPreviewPayload(TypedDict):
    type: Literal["json"]
    data: Any

class ImagePreviewPayload(TypedDict):
    type: Literal['image']
    data: str | List[str]

class MediaPreviewPayload(TypedDict):
    type: Literal["image", 'video', 'audio', 'markdown', "iframe", "html"]
    data: str

class DefaultPreviewPayload:
    type: str
    data: Any

PreviewPayload: TypeAlias = Union[
    TablePreviewPayload,
    TextPreviewPayload,
    JSONPreviewPayload,
    ImagePreviewPayload,
    MediaPreviewPayload,
    DefaultPreviewPayload
]
