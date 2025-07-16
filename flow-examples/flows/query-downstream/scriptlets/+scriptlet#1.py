from oocana import Context

#region generated meta
import typing
Inputs = typing.Dict[str, typing.Any]
class Outputs(typing.TypedDict):
    output: typing.Any
#endregion

async def main(params: Inputs, context: Context) -> Outputs:

    result = await context.query_downstream()

    print("query result:", result)

    # TODO: more test detail

    return { "output": "output_value" }
