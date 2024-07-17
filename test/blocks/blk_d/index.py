from oocana import Context


count = 1

def main(inputs, context: Context):

    print(f"inputs: {inputs}")
    print(f"module count: {count}")

    return {"output": count}
