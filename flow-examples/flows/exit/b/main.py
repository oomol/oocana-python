from oocana import Context
import time

def main(inputs, context: Context):

    a = object()

    for i in range(11):
        context.report_progress(i * 10)
        time.sleep(0.1)
    # TODO: example 里暂时只能跑成功的，不支持测试失败的情况。等支持了，再添加失败测试
    # exit(1)
    return {"a": a}