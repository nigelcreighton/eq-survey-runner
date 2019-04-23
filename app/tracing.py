import wrapt
from aws_xray_sdk.core import xray_recorder


def trace():
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        # AWS X-Ray tracing
        if True:
            xray_recorder.begin_subsegment(wrapped.__name__)
            result = wrapped(*args, **kwargs)
            xray_recorder.end_subsegment()
            return result

        return wrapped(*args, **kwargs)

    return wrapper
