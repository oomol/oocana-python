from oocana import Context

async def main(inputs, context: Context):

    progress_callback_called_count = 0

    def set_progress_callback(progress):
        nonlocal progress_callback_called_count
        progress_callback_called_count += 1
        print("progress callback", progress)

    block_job = context.run_block("blk_b", inputs={"my_input": "111"})
    block_job.add_output_callback(lambda output: print("output callback", output))
    block_job.add_progress_callback(set_progress_callback)
    await block_job.finish()

    block_job = context.run_block("blk_bccc", inputs={"my_input": "111"})

    failed = False
    try:
        await block_job.finish()
    except Exception as e:
        failed = True
        print("Expected error:", e)

    assert failed, "Expected error, but run_res finished successfully"
    assert progress_callback_called_count > 1, "Progress callback was called " + str(progress_callback_called_count) + " times, expected more than 1 time"


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