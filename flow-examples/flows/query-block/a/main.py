from oocana import Context

async def main(inputs, context: Context):

    run_res = await context.query_block("blk_b")
    assert run_res is not None

    assert isinstance(run_res, dict), "Expected run result to be a dictionary"
    assert "inputs_def" in run_res, "Expected 'inputs_def' key to be present in the run result"
    assert "outputs_def" in run_res, "Expected 'outputs_def' key to be present in the run result"
    assert "additional_outputs" in run_res, "Expected 'additional_outputs' key to be present in the run result"
    assert "additional_inputs" in run_res, "Expected 'additional_inputs' key to be present in the run result"

    fail = False
    try:
        run_res = await context.query_block("blk_b_non_existent")
    except Exception as e:
        fail = True
        print("Error occurred while querying block:", e)

    assert fail, "Expected an error when querying a non-existent block"

    return {"a": "a"}