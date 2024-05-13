import sys
import random
import asyncio
import contextvars

var = contextvars.ContextVar('sdk', default=None)

original_stdout_write = sys.stdout.write
original_stderr_write = sys.stderr.write

# TODO: 问题在于 print 调用 write 时，是每个参数单独转为 str 后调一次 API。每一次调用并不代表就是完整一行，需要自己做个 buffer，读到换行符时，再调用上报一行。
def hook_stdout_write(s):
    sdk = var.get()
    # for line in s.splitlines():
    original_stdout_write(sdk + ":" + s + "\n")

def hook_stderr_write(s):
    sdk = var.get()
    # for line in s.splitlines():
    original_stderr_write(sdk + ":" + s + "\n")

sys.stdout.write = hook_stdout_write
sys.stderr.write = hook_stderr_write

async def echo(name="world"):
    var.set(name)
    await asyncio.sleep(random.randint(1, 3))
    print('This is stdout in', name)
    await asyncio.sleep(random.randint(1, 3))
    print("Error message in", name, file=sys.stderr)

async def main():
    await asyncio.gather(echo("foo"), echo("bar"))

if __name__ == '__main__':
    asyncio.run(main())