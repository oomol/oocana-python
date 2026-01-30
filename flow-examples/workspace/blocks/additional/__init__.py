from oocana import Context


def main(inputs: dict, context: Context):
    print("inputs_def", context.inputs_def)
    print("outputs_def", context.outputs_def)

    merged = ""
    for key in context.inputs_def:
        value = inputs.get(key)
        if value is not None:
            merged += str(value)

    result = {}
    for key in context.outputs_def:
        result[key] = merged

    return result
