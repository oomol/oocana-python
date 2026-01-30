from oocana import Context

def main(inputs: dict, context: Context):
    # Validate that the input is None (null value from nullable input)
    if inputs.get("input") is None:
        print("Input is None as expected")
    else:
        raise Exception("Expected None for nullable input")

    return {"output": "output_value"}
