from oocana import Context

def main(inputs: dict, context: Context):
    # End node: receives output from +python#1 and passes through
    return {"output": inputs.get("input")}
