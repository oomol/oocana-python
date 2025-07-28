from oocana import Context

#region generated meta
import typing
Inputs = typing.Dict[str, typing.Any]
class Outputs(typing.TypedDict):
    output1: typing.Any
#endregion

def main(params: Inputs, context: Context) -> Outputs:
    context.output("output1", "Hello World", to_node=[{"node_id": "end", "input_handle": "k"}])
