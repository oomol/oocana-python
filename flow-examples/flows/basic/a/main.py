from oocana import Context
import time

def main(inputs, context: Context):

    a = object()

    for i in range(11):
        context.report_progress(i * 10)
        time.sleep(0.1)
    context.logger.info("a is a object")

    return {"a": a}