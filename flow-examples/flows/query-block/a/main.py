from oocana import Context

async def main(inputs, context: Context):

    run_res = await context.query_block("blk_b")
    assert run_res is not None

    fail = False
    try:
        run_res = await context.query_block("blk_b_non_existent")
    except Exception as e:
        fail = True
        print("Error occurred while querying block:", e)

    assert fail, "Expected an error when querying a non-existent block"

    return {"a": "a"}