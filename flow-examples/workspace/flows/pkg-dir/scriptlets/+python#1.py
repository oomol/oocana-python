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

    assert(context.pkg_dir is not None)

    # check if tmp_dir is exist
    if not os.path.exists(context.pkg_dir):
        raise Exception(f"tmp_dir {context.pkg_dir} is not exist")

    return { "output": "output_value" }
