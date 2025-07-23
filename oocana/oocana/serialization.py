from typing import TYPE_CHECKING, TypedDict, Literal
from os import remove
from os.path import exists, join

__all__ = ["CompressionOptions", "setup_dataframe_serialization", "compression_options", "compression_suffix"]

SUPPORTED_COMPRESSION_METHODS = ["zip", "gzip", "bz2", "zstd", "xz", "tar"]
class CompressionOptions(TypedDict):
    """Options for compression methods used in serialization.
    """

    method: Literal["zip", "gzip", "bz2", "zstd", "xz", "tar"] | None
    """The compression method to use. If None, no compression is applied.
    Supported methods are: zip, gzip, bz2, zstd, xz, tar.
    If use zstd, please install zstandard library otherwise it will raise ImportError.
    For more information or other compression options, see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_pickle.html
    """

if TYPE_CHECKING:
    from .context import Context


def setup_dataframe_serialization(context: 'Context', compression: CompressionOptions | None = None) -> None:
    """
    Setup the DataFrame serialization for the compression operation. This function needs to be called before using DataFrame serialization. 
    This function ensures that DataFrames are serialized to a special file based on the specified compression method.
    The configuration is stored in the `__compression_options.json` file in the pkg_data_dir. So it can be persisted across sessions
    and stored in the session directory for later retrieval.
    """
    try:
        if compression is None:
            if exists(join(context.pkg_data_dir, COMPRESSION_OPTIONS_FILE)):
                remove(join(context.pkg_data_dir, COMPRESSION_OPTIONS_FILE))
            return
        elif compression["method"] not in SUPPORTED_COMPRESSION_METHODS:
            raise ValueError(f"Unsupported compression method: {compression['method']}. Supported methods are: {SUPPORTED_COMPRESSION_METHODS}.")
        elif compression is not None and compression["method"] == "zstd":
            # If zstd compression is specified, ensure that the zstandard library is available.
            try:
                import zstandard as zstd  # type: ignore
            except ImportError:
                raise ImportError("To use zstd compression, please install the zstandard library.")
        
        # write compression options to a file if exist then overwrite it
        with open(join(context.pkg_data_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            import json
            json.dump(compression, f)
        
    except ImportError:
        raise ImportError("To Setup DataFrame serialization, pandas is required. Please install it with `poetry install pandas`.")

COMPRESSION_OPTIONS_FILE = "__compression_options.json"

def compression_options(context: 'Context') -> CompressionOptions | None:
    """
    Retrieve the compression options from the session directory.
    If no options are set, return None.
    """
    import json
    try:
        with open(join(context.pkg_data_dir, COMPRESSION_OPTIONS_FILE), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from compression options file. Returning None.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading compression options: {e}. Returning None.")
        return None
    
def compression_suffix(context: 'Context') -> str:
    """
    Get the file suffix based on the compression method.
    If no compression is specified, return an empty string.
    """
    compression = compression_options(context)

    if compression is None or compression["method"] is None:
        return ".pkl"
    
    method = compression["method"]
    if method == "zip":
        return ".zip"
    elif method == "gzip":
        return ".gz"
    elif method == "bz2":
        return ".bz2"
    elif method == "zstd":
        return ".zst"
    elif method == "xz":
        return ".xz"
    elif method == "tar":
        return ".tar"
    else:
        return ".pkl"  # Default case if method is not recognized