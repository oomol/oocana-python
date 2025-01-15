
from typing import Any, TypedDict, List, Literal, TypeAlias, Union, Protocol, runtime_checkable

__all__ = ["PreviewPayload", "TablePreviewPayload", "TextPreviewPayload", "JSONPreviewPayload", "ImagePreviewPayload", "MediaPreviewPayload", "PandasPreviewPayload", "DefaultPreviewPayload"]

# this class is for pandas.DataFrame
@runtime_checkable
class DataFrame(Protocol):

    def __dataframe__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def to_dict(self, *args: Any, **kwargs: Any) -> Any:
        ...

@runtime_checkable
class JsonAble(Protocol):

    def to_json(self, *args: Any, **kwargs: Any) -> Any:
        ...

@runtime_checkable
class ShapeDataFrame(DataFrame, Protocol):

    @property
    def shape(self) -> tuple[int, int]:
        ...

@runtime_checkable
class PartialDataFrame(Protocol):
    def head(self, *args: Any, **kwargs: Any) -> JsonAble:
        ...
    
    def tail(self, *args: Any, **kwargs: Any) -> JsonAble:
        ...

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

class PandasPreviewPayload(TypedDict):
    type: Literal['table']
    data: DataFrame

class DefaultPreviewPayload:
    type: str
    data: Any

PreviewPayload: TypeAlias = Union[
    TablePreviewPayload,
    TextPreviewPayload,
    JSONPreviewPayload,
    ImagePreviewPayload,
    MediaPreviewPayload,
    DataFrame,
    PandasPreviewPayload,
    DefaultPreviewPayload
]