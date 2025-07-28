from oocana import Context
import time

def main(inputs, context: Context):

    context.output("a", "output")
    context.outputs({"a": "outputs"})

    return {"a": "finished"}