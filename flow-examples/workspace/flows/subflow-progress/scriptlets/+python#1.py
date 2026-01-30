from oocana import Context

def main(inputs: dict, context: Context):
    return {"output": inputs.get("output", "passthrough")}
