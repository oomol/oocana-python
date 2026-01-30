from oocana import Context


def main(inputs: dict, context: Context):
    print("end node inputs:", inputs)
    return {
        "output": inputs.get("input") + inputs.get("output1"),
    }
