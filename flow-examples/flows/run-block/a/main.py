from oocana import Context

async def main(inputs, context: Context):

    run_res = context.run_block("blk_b", {"my_input": "111"})
    run_res.add_event_callback(lambda payload: print("event callback", payload))
    run_res.add_output_callback(lambda handle, value: print("output callback", handle, value))
    res = await run_res.finish()
    assert res.get("error") is None

    run_res = context.run_block("blk_bccc", {"my_input": "111"})
    res = await run_res.finish()
    assert res.get("error") is not None

    return {"a": "a"}