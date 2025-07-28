from oocana import Context

async def main(inputs, context: Context):

    block_job = context.run_block("self::basic", inputs={"input": "111"})
    block_job.add_output_callback(lambda output: print("output callback", output))
    await block_job.finish()

    return {"a": "a"}