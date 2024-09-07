from oocana import Context

def main(props, context: Context):
    print("Hello from Python blk_b")
    if "my_input" in props:
        i = props["my_input"]
        if isinstance(i, object) and not isinstance(i, dict):
            print("my_input is a object and not a dict", i)
        else:
            print("my_input is not a object", i)

    context.output("my_output", 11)
