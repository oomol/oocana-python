import time
import threading

def throttle(period):
    last_invoke_time = 0
    timer = None
    last_args = None
    last_kwargs = None

    def decorator(fn):
        def wrapper(*args, **kwargs):
            nonlocal last_invoke_time, timer, last_args, last_kwargs
            now = time.time()
            should_invoke = now - last_invoke_time > period

            def invoke(args, kwargs):
                nonlocal last_invoke_time
                last_invoke_time = time.time()
                return fn(*args, **kwargs)

            if should_invoke:
                if timer:
                    timer.cancel()
                    timer = None
                last_invoke_time = now
                return fn(*args, **kwargs)
            else:
                last_args = args
                last_kwargs = kwargs
                if timer:
                    timer.cancel()
                timer = threading.Timer(period - (now - last_invoke_time), lambda: invoke(last_args, last_kwargs))
                timer.start()

        return wrapper
    return decorator
