from oocana import Context


def main(inputs, context: Context):
    value = inputs.get("input", "default")
    context.send_message(f"two_params received: {value}")
    return {"output": f"two_params:{value}"}
