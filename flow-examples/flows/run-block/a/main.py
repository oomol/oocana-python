from oocana import Context

async def main(inputs, context: Context):

    run_res = context.run_block("blk_b", inputs={"my_input": "111"})
    run_res.add_event_callback(lambda payload: print("event callback", payload))
    run_res.add_output_callback(lambda handle, value: print("output callback", handle, value))
    res = await run_res.finish()
    assert res.get("error") is None

    run_res = context.run_block("blk_bccc", inputs={"my_input": "111"})
    res = await run_res.finish()
    assert res.get("error") is not None


    run_res = context.run_block("self::inputs", inputs={"schema_input": 111, "nullable_input": None, "default_input": "default_value"})
    res = await run_res.finish()
    assert res.get("error") is not None

    run_res = context.run_block("self::inputs", inputs={"schema_input": "aaa"})
    res = await run_res.finish()
    assert res.get("error") is None

    return {"a": "a"}