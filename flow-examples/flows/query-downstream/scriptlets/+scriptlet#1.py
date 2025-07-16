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

    assert isinstance(result, dict), "Expected result to be a dictionary"
    assert "output1" in result, "Expected 'output1' key to be present in the result"
    output1 = result["output1"]
    assert "to_node" in output1, "Expected 'to_node' key to be present in the result"
    node_upstream = output1["to_node"]
    assert isinstance(node_upstream, list), "Expected 'to_node' to be a list"
    assert len(node_upstream) > 0, "Expected 'to_node' list to contain at least one node"

    first_upstream_node = node_upstream[0]
    assert isinstance(first_upstream_node, dict), "Expected first upstream node to be a dictionary"
    assert first_upstream_node.get("node_id") == "end", "Expected first upstream node to have node_id 'end'"
    assert first_upstream_node.get("description") == "this is a downstream node", "Expected first upstream node to have description"
    assert first_upstream_node.get("input_handle") == "output1", "Expected first upstream node to have input_handle 'output1'"
    input_handle_def = first_upstream_node.get("input_handle_def")
    assert isinstance(input_handle_def, dict), "Expected input_handle_def to be a dictionary"
    assert input_handle_def.get("handle") == "output1", "Expected input_handle_def to have handle 'output1'"
    assert input_handle_def.get("description") == "this is a description for handle", "Expected input_handle_def to have description"

    return { "output": "output_value" }
