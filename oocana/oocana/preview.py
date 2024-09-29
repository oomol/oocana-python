
from typing import Any, TypedDict, List, Literal, TypeAlias

class TablePreviewData(TypedDict):
    columns: List[str | int | float]
    rows: List[List[str | int | float | bool]]
    row_count: int | None

class TablePreviewPayload(TypedDict):
    type: Literal['table']
    data: TablePreviewData | Any

class MediaPreviewPayload(TypedDict):
    type: Literal['image', 'audio', 'video', 'markdown', "iframe"]
    data: str

PreviewPayload: TypeAlias = TablePreviewPayload | MediaPreviewPayload | Any