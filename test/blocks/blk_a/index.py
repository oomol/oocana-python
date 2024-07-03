import datetime
from oocana import Context

def main(props, context: Context):

    context.send_message("Hello from Python blk_a")
    context.log_json({"message": "Hello from Python blk_a"})
    obj = datetime.datetime.now()
    return {
        "my_output": obj
    }
