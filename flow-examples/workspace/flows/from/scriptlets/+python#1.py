from oocana import Context

def main(inputs: dict, context: Context):
    # Receives inputs from three sources:
    # - input: direct value (2)
    # - output: from +python#2 node (3)
    # - value1: from +value#1 node (4), with fallback value 5
    input_val = inputs.get("input")
    output_val = inputs.get("output")
    value1_val = inputs.get("value1")

    result = input_val + output_val + value1_val
    print(f"Calculating: {input_val} + {output_val} + {value1_val} = {result}")

    return {"output": result}
