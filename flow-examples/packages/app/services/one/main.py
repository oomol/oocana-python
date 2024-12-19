from oocana import ServiceContextAbstractClass

def block_a_handler(inputs: dict, context):
    print("Hello from block_a_handler")
    return {"two": "22"}

def main(service: ServiceContextAbstractClass):
    print("Hello from service")
    service.block_handler = {
        "a": block_a_handler,
    }