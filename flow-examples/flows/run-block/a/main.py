from oocana import Context

async def main(inputs, context: Context):

    events = await context.run_block("blk_b", {"my_input": "111"})
    context.log_json({"events": events})

    return {"a": "a"}