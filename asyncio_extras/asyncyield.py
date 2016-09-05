from collections import Coroutine
from typing import Optional

__all__ = ('yield_async',)


class _AsyncYieldValue:
    __slots__ = 'value'

    def __init__(self, value):
        self.value = value

    def __await__(self):
        yield self


async def work_coroutine(
        coro: Coroutine, exception: BaseException = None) -> Optional[_AsyncYieldValue]:
    """
    Run the coroutine until it does ``await yield_async(...)``.

    :return: the value contained by :class:`_AsyncYieldValue`, or ``None`` if the coroutine has
        finished

    """
    value = None
    while True:
        try:
            if exception is not None:
                value = coro.throw(exception)
            else:
                value = coro.send(value)
        except StopIteration:
            return None

        if isinstance(value, _AsyncYieldValue):
            return value
        else:
            try:
                value = await value
            except Exception as e:
                exception = e
            else:
                exception = None


def yield_async(value=None):
    """The equivalent of ``yield`` in an asynchronous context manager or asynchronous generator."""
    return _AsyncYieldValue(value)
