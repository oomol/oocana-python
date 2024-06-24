from oocana import AppletContext, Context

def main(applet_context: AppletContext):
    def one(payload, context: Context):
        context.send_message("block one is running")
        return {
            "a": "a",
        }
        
    applet_context['block_handler'] = {
        "one": one
    }
