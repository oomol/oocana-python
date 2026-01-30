from oocana import Context

def main(inputs: dict, context: Context):
    # Receive output from first node and validate nullable input1
    return {"output": inputs.get("input")}
