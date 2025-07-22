from typing import TypedDict, Literal

__all__ = ["CompressionOptions", "setup_dataframe_serialization", "compression_options", "compression_suffix"]


class CompressionOptions(TypedDict):
    """Options for compression methods used in serialization.
    """

    method: Literal["zip", "gzip", "bz2", "zstd", "xz", "tar"] | None
    """The compression method to use. If None, no compression is applied.
    Supported methods are: zip, gzip, bz2, zstd, xz, tar.
    If use zstd, please install zstandard library otherwise it will raise ImportError.
    For more information or other compression options, see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_pickle.html
    """

def setup_dataframe_serialization(compression: CompressionOptions | None = None) -> None:
    """
    Setup the DataFrame serialization for the compression module.
    This function ensures that DataFrames are serialized to pickle files
    and stored in the session directory for later retrieval.
    """
    try:
        if compression is None:
            # remove compression options file if it exists
            try:
                import os
                os.remove(COMPRESSION_OPTIONS_FILE)
            except FileNotFoundError:
                # If the file does not exist, we simply ignore the error.
                pass
            return
        elif compression["method"] not in ["zip", "gzip", "bz2", "zstd", "xz", "tar"]:
            raise ValueError(f"Unsupported compression method: {compression['method']}. Supported methods are: zip, gzip, bz2, zstd, xz, tar.")
        elif compression is not None and compression["method"] == "zstd":
            # If zstd compression is specified, ensure that the zstandard library is available.
            try:
                import zstandard as zstd
            except ImportError:
                raise ImportError("To use zstd compression, please install the zstandard library.")
        
        # write compression options to a file if exist then overwrite it
        with open(COMPRESSION_OPTIONS_FILE, "w") as f:
            import json
            json.dump(compression, f)
        


    except ImportError:
        raise ImportError("To Setup DataFrame serialization, pandas is required. Please install it with `poetry install pandas`.")
    

# 设置一个常量地址
COMPRESSION_OPTIONS_FILE = "compression_options.json"


def compression_options() -> CompressionOptions | None:
    """
    Retrieve the compression options from the session directory.
    If no options are set, return None.
    """
    import json
    try:
        with open(COMPRESSION_OPTIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from compression options file. Returning None.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading compression options: {e}. Returning None.")
        return None
    
def compression_suffix() -> str:
    """
    Get the file suffix based on the compression method.
    If no compression is specified, return an empty string.
    """
    compression = compression_options()

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