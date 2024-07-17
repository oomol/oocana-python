from oocana import Context


count = 1

def main(inputs, context: Context):

    global count
    print(f"inputs: {inputs}")
    print(f"module count: {count}")

    count += 1

    return {"output": count}