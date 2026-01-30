from oocana import Context
import time

def main(inputs: dict, context: Context):
    for i in range(4):
        context.report_progress(i * 25)
        time.sleep(0.5)

    return {"output": inputs.get("output", "default")}
