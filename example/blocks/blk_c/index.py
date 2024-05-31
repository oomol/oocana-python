import datetime
from oocana import Context

def main(props, context: Context):

    context.send_message("Hello from Python blk_a")
    context.log_json({"message": "Hello from Python blk_a"})
    obj = datetime.datetime.now()
    print("obj", obj)
    context.output(obj, "my_output")
    context.output("321321", "my_output1")
    context.done()
