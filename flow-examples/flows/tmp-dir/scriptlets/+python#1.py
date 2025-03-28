#region generated meta
import typing
class Inputs(typing.TypedDict):
    input: str
class Outputs(typing.TypedDict):
    output: str
#endregion

from oocana import Context

def main(params: Inputs, context: Context) -> Outputs:

    assert(context.tmp_dir is not None)

    return { "output": "output_value" }
