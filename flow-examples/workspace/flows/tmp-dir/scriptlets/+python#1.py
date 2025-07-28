from oocana import Context
import os.path
#region generated meta
import typing
class Inputs(typing.TypedDict):
    input: str
class Outputs(typing.TypedDict):
    output: str
#endregion

def main(params: Inputs, context: Context) -> Outputs:

    assert(context.tmp_dir is not None)
    assert(context.tmp_pkg_dir is not None)

    # check if tmp_dir is exist
    if not os.path.exists(context.tmp_dir):
        raise Exception(f"tmp_dir {context.tmp_dir} is not exist")
    # check if tmp_pkg_dir is exist
    if not os.path.exists(context.tmp_pkg_dir):
        raise Exception(f"tmp_pkg_dir {context.tmp_pkg_dir} is not exist") 

    return { "output": "output_value" }
