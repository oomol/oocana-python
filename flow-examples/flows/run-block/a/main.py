from oocana import Context

async def main(inputs, context: Context):

    block_job = context.run_block("blk_b", inputs={"my_input": "111"})
    block_job.add_output_callback(lambda output: print("output callback", output))
    await block_job.finish()

    block_job = context.run_block("blk_bccc", inputs={"my_input": "111"})

    failed = False
    try:
        await block_job.finish()
    except Exception as e:
        failed = True
        print("Expected error:", e)

    assert failed, "Expected error, but run_res finished successfully"


    block_job = context.run_block("self::inputs", inputs={"schema_input": 111, "nullable_input": None, "default_input": "default_value"}, strict=True)

    strict_failed = False
    try:
        await block_job.finish()
    except Exception as e:
        strict_failed = True
        print("Expected error:", e)

    assert strict_failed, "Expected error, but run_res finished successfully"


    block_job = context.run_block("self::inputs", inputs={"schema_input": "aaa"})
    await block_job.finish()

    return {"a": "a"}