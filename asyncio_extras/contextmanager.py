from collections import Coroutine
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable

from asyncio_extras.asyncyield import work_coroutine

__all__ = ('async_contextmanager',)


class _AsyncContextManager:
    __slots__ = 'coroutine'

    def __init__(self, coroutine: Coroutine):
        self.coroutine = coroutine

    async def __aenter__(self):
        retval = await work_coroutine(self.coroutine)
        if retval is not None:
            return retval.value
        else:
            raise RuntimeError('coroutine finished without yielding a value')

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        retval = await work_coroutine(self.coroutine, exc_val)
        if retval is not None:
            raise RuntimeError('coroutine yielded a value in the exit phase: {!r}'.
                               format(retval.value))


def async_contextmanager(func: Callable[..., Coroutine]) -> Callable:
    """
    Transform a coroutine function into something that works with ``async with``.

    The coroutine may yield any number of awaitables which are resolved and sent back to the
    coroutine. To indicate that the setup phase is complete, the coroutine must use
    :func:`~yield_async` *exactly once* . The rest of the coroutine will then be processed after
    the context block has been executed. If the context was exited with an exception, this
    exception will be raised in the coroutine.

    For example::

        @async_contextmanager
        async def mycontextmanager(arg):
            context = await setup_remote_context(arg)
            await yield_async(context)
            await context.teardown()

        async def frobnicate(arg):
            async with mycontextmanager(arg) as context:
                do_something_with(context)

    :param func: a coroutine function
    :return: a callable that can be used with ``async with``

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return _AsyncContextManager(func(*args, **kwargs))

    assert iscoroutinefunction(func), '"func" must be a coroutine function'
    return wrapper
