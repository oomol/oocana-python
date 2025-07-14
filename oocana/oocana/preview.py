
from typing import Any, TypedDict, List, Literal, TypeAlias, Union, Protocol, runtime_checkable

__all__ = ["PreviewPayload", "PreviewPayloadInternal", "TablePreviewPayload", "TextPreviewPayload", "JSONPreviewPayload", "ImagePreviewPayload", "MediaPreviewPayload", "PandasPreviewPayload", "DefaultPreviewPayload"]

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

    def to_csv(self, path_or_buf=None, *, sep=',', na_rep='', float_format=None, columns=None, header=True, index=True, index_label=None, mode='w', encoding=None, compression='infer', quoting=None, quotechar='"', lineterminator=None, chunksize=None, date_format=None, doublequote=True, escapechar=None, decimal='.', errors='strict', storage_options=None) -> None | str:
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
    id: str | None

class TextPreviewPayload(TypedDict):
    type: Literal["text"]
    data: Any
    id: str | None

class JSONPreviewPayload(TypedDict):
    type: Literal["json"]
    data: Any
    id: str | None

class ImagePreviewPayload(TypedDict):
    type: Literal['image']
    data: str | List[str]
    id: str | None

class MediaPreviewPayload(TypedDict):
    type: Literal["image", 'video', 'audio', 'markdown', "iframe", "html"]
    data: str
    id: str | None

class PandasPreviewPayload(TypedDict):
    type: Literal['table']
    data: DataFrame
    id: str | None

class CsvPreviewPayload(TypedDict):
    type: Literal['csv']
    data: str # csv file path
    id: str | None

class DefaultPreviewPayload(TypedDict):
    type: str
    data: Any
    id: str | None

PreviewPayloadInternal: TypeAlias = Union[
    TablePreviewPayload,
    TextPreviewPayload,
    JSONPreviewPayload,
    ImagePreviewPayload,
    MediaPreviewPayload,
    CsvPreviewPayload,
    PandasPreviewPayload,
    DefaultPreviewPayload
]

PreviewPayload: TypeAlias = Union[
    TablePreviewPayload,
    TextPreviewPayload,
    JSONPreviewPayload,
    ImagePreviewPayload,
    MediaPreviewPayload,
    CsvPreviewPayload,
    DataFrame,
    PandasPreviewPayload,
    DefaultPreviewPayload
]