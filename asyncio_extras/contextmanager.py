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
    Wrap a function into a callable that creates asynchronous context managers.

    The coroutine may yield any number of awaitables which are resolved and sent back to the
    coroutine. To indicate that the setup phase is complete, the coroutine must use
    :func:`~yield_async` *exactly once* . The rest of the coroutine will then be processed
    after the context block has been executed. If the context was exited with an exception,
    this exception will be raised in the coroutine.

    For example (Python 3.5 and earlier)::

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

    :param func: an async generator function or a coroutine function using ``yield_async()``
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
