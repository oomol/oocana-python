from oocana import Context

def main(params, context: Context):
    return {
        "nullable_output": params.get("nullable_input"),
        "default_output": params.get("default_input")
    }