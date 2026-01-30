from oocana import Context

def main(inputs: dict, context: Context):
    # Return 'c' which is not defined in outputs_def
    # This should trigger a BlockWarning event
    return {"a": "a", "b": "b", "c": "c"}
