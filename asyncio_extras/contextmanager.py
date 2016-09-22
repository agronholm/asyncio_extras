from collections.abc import Coroutine
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Union

from asyncio_extras.asyncyield import work_coroutine

__all__ = ('async_contextmanager',)

try:
    from inspect import isasyncgen, isasyncgenfunction
    from types import AsyncGeneratorType

    generator_types = Union[Coroutine, AsyncGeneratorType]
except ImportError:
    def isasyncgen(func):
        return False

    isasyncgenfunction = isasyncgen
    generator_types = Coroutine


class _NativeAsyncContextManager:
    __slots__ = 'generator'

    def __init__(self, generator) -> None:
        self.generator = generator

    def __aenter__(self):
        return self.generator.asend(None)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            await self.generator.athrow(exc_val)
        else:
            try:
                await self.generator.asend(None)
            except StopAsyncIteration:
                pass
            else:
                raise RuntimeError("async generator didn't stop")


class _EmulatedAsyncContextManager:
    __slots__ = 'coroutine'

    def __init__(self, coroutine: Coroutine) -> None:
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
            raise RuntimeError("async generator didn't stop")


def async_contextmanager(func: Callable[..., generator_types]) -> Callable:
    """
    Transform a coroutine function into something that works with ``async with``.

    This is an asynchronous counterpart to :func:`~contextlib.contextmanager`.
    The wrapped function can either be a native async generator function (``async def`` with
    ``yield``) or, if your code needs to be compatible with Python 3.5, you can use
    :func:`~asyncio_extras.asyncyied.yield_async` instead of the native ``yield`` statement.

    The generator must yield *exactly once*, just like with :func:`~contextlib.contextmanager`.

    Usage in Python 3.5 and earlier::

        @async_contextmanager
        async def mycontextmanager(arg):
            context = await setup_remote_context(arg)
            await yield_async(context)
            await context.teardown()

        async def frobnicate(arg):
            async with mycontextmanager(arg) as context:
                do_something_with(context)

    The same context manager function in Python 3.6+::

        @async_contextmanager
        async def mycontextmanager(arg):
            context = await setup_remote_context(arg)
            yield context
            await context.teardown()

    :param func: an async generator function or a coroutine function using
        :func:`~asyncio_extras.asyncyied.yield_async`
    :return: a callable that can be used with ``async with``

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        generator = func(*args, **kwargs)
        if isasyncgen(generator):
            return _NativeAsyncContextManager(generator)
        else:
            return _EmulatedAsyncContextManager(generator)

    assert isasyncgenfunction(func) or iscoroutinefunction(func),\
        '"func" must be an async generator function or a coroutine function'
    return wrapper
