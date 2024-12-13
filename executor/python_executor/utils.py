import threading
import asyncio
from typing import Callable, Awaitable, Any

def run_async_code(async_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(async_func)
    finally:
        loop.close()

def run_async_code_and_loop(async_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(async_func)
        loop.run_forever()
    finally:
        loop.close()

def run_in_new_thread(async_func: Callable[[], Awaitable[Any]]):
    threading.Thread(target=run_async_code, args=(async_func(),)).start()

def loop_in_new_thread(async_func: Callable[[], Awaitable[Any]]):
    threading.Thread(target=run_async_code_and_loop, args=(async_func(),)).start()

def oocana_dir() -> str:
    from os.path import expanduser, join
    return join(expanduser("~"), ".oocana")