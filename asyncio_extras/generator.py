from collections import Coroutine, AsyncIterator
from functools import wraps
from inspect import iscoroutinefunction, isfunction
from typing import Callable

from asyncio_extras.asyncyield import work_coroutine

__all__ = ('async_generator', 'isasyncgeneratorfunction')


class _AsyncGeneratorWrapper:
    __slots__ = 'coroutine'

    def __init__(self, coroutine: Coroutine):
        self.coroutine = coroutine

    async def __aiter__(self):
        return self

    async def __anext__(self):
        value = await work_coroutine(self.coroutine)
        if value is not None:
            return value.value
        else:
            raise StopAsyncIteration


def async_generator(func: Callable[..., Coroutine]) -> Callable[..., AsyncIterator]:
    """
    Transform a coroutine function into something that works with the ``async for``.

    Any awaitable yielded by the given coroutine function will be awaited on and the result passed
    back to the coroutine. Any other yielded values will be yielded to the actual consumer of the
    asynchronous iterator.

    For example::

        @async_generator
        async def mygenerator(websites):
            for website in websites:
                page = await http_fetch(website)
                await yield_async(page)

        async def fetch_pages():
            websites = ('http://foo.bar', 'http://example.org')
            async for sanitized_page in mygenerator(websites):
                print(sanitized_page)

    :param func: a coroutine function
    :return: a callable that returns an async iterator

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return _AsyncGeneratorWrapper(func(*args, **kwargs))

    assert iscoroutinefunction(func), '"func" must be a coroutine function'
    wrapper._is_async_generator = True
    return wrapper


def isasyncgeneratorfunction(obj) -> bool:
    """Return ``True`` if the given object is an asynchronous generator function."""
    return isfunction(obj) and getattr(obj, '_is_async_generator', False)
