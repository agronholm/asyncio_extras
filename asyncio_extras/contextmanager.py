from collections.abc import Coroutine
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Union

from async_generator import async_generator, isasyncgenfunction

try:
    from types import AsyncGeneratorType

    generator_types = Union[Coroutine, AsyncGeneratorType]
except ImportError:
    generator_types = Coroutine

__all__ = ('async_contextmanager',)


class _AsyncContextManager:
    __slots__ = 'generator'

    def __init__(self, generator) -> None:
        self.generator = generator

    def __aenter__(self):
        return self.generator.asend(None)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            try:
                await self.generator.athrow(exc_val)
            except StopAsyncIteration:
                pass

            return True
        else:
            try:
                await self.generator.asend(None)
            except StopAsyncIteration:
                pass
            else:
                raise RuntimeError("async generator didn't stop")


def async_contextmanager(func: Callable[..., generator_types]) -> Callable:
    """
    Transform a coroutine function into something that works with ``async with``.

    This is an asynchronous counterpart to :func:`~contextlib.contextmanager`.
    The wrapped function can either be a native async generator function (``async def`` with
    ``yield``) or, if your code needs to be compatible with Python 3.5, you can use
    :func:`~async_generator.yield_` instead of the native ``yield`` statement.

    The generator must yield *exactly once*, just like with :func:`~contextlib.contextmanager`.

    Usage in Python 3.5 and earlier::

        @async_contextmanager
        async def mycontextmanager(arg):
            context = await setup_remote_context(arg)
            await yield_(context)
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
        :func:`~async_generator.yield_`
    :return: a callable that can be used with ``async with``

    """
    if not isasyncgenfunction(func):
        if iscoroutinefunction(func):
            func = async_generator(func)
        else:
            '"func" must be an async generator function or a coroutine function'

    @wraps(func)
    def wrapper(*args, **kwargs):
        generator = func(*args, **kwargs)
        return _AsyncContextManager(generator)

    return wrapper
