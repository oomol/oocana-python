
from typing import Any, TypedDict, List, Literal, TypeAlias, Union, Protocol, runtime_checkable

__all__ = ["PreviewPayload", "TablePreviewPayload", "TextPreviewPayload", "JSONPreviewPayload", "ImagePreviewPayload", "MediaPreviewPayload", "PandasPreviewPayload", "DefaultPreviewPayload"]

@runtime_checkable
class DataFrameIndex(Protocol):
    def tolist(self) -> Any:
        ...

# this class is for pandas.DataFrame
@runtime_checkable
class DataFrame(Protocol):

    def __len__(self) -> int:
        ...

    def __dataframe__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @property
    def index(self) -> DataFrameIndex:
        ...

    def to_json(self, orient: Literal["split"]) -> str:
        ...

    def to_dict(self, orient: Literal["split"]) -> Any:
        ...

@runtime_checkable
class ShapeDataFrame(DataFrame, Protocol):

    @property
    def shape(self) -> tuple[int, int]:
        ...

@runtime_checkable
class PartialDataFrame(DataFrame, Protocol):
    def head(self, count: int) -> DataFrame:
        ...
    
    def tail(self, count: int) -> DataFrame:
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