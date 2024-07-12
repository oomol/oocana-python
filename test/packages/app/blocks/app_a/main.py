from oocana import ServiceContext, Context

def main(service_context: ServiceContext):
    def one(payload, context: Context):
        context.send_message("block one is running")
        return {
            "a": "a",
        }
        
    service_context['block_handler'] = {
        "one": one
    }
