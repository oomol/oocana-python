import datetime

def main(props, context):

    context.send_message("Hello from Python blk_a")
    context.log_json({"message": "Hello from Python blk_a"})
    obj = datetime.datetime.now()
    print("obj", obj)
    context.output(obj, "my_output", True)
