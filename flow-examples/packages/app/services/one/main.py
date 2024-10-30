from oocana import ServiceContextAbstractClass

def block_a_handler(inputs: dict, context):
    print("Hello from block_a_handler")
    return {"two": "22"}

def block_b_handler(inputs: dict, context):
    print("Hello from block_b_handler")
    return {"two": "2222", "one": "11111"}

def main(service: ServiceContextAbstractClass):
    print("Hello from service")
    service.block_handler = {
        "a": block_a_handler,
        "b": block_b_handler
    }