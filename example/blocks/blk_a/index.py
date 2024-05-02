import datetime

def main(props, context):

    context.send_message("Hello from Python blk_a")
    context.log_json({"message": "Hello from Python blk_a"})
    obj = datetime.datetime.now()
    print("obj", obj)
    context.output("122", "my_output")
    context.output("321321", "my_output1")
    context.done()
