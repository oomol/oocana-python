from oocana import Context


def main(context: Context):
    value = context.inputs.get("input", "default")
    return {"output": f"context_only:{value}"}
