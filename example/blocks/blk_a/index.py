
def main(props, context):
    # print("Hello from Python blk_a", props)
    context.send_message("Hello from Python blk_a")
    context.log_json({"message": "Hello from Python blk_a"})
    # context.send_error("Hello from Python blk_a")
    context.result(11, "my_output", True)
