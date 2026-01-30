from oocana import Context


async def main(inputs, context: Context):
    value = inputs.get("input", "default")
    context.send_message(f"async_two_params received: {value}")
    return {"output": f"async_two_params:{value}"}
