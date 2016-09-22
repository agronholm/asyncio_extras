import inspect
import sys
from collections.abc import Coroutine, AsyncIterator
from functools import wraps
from inspect import iscoroutinefunction, isfunction
from typing import Callable
from warnings import warn

from asyncio_extras.asyncyield import work_coroutine

__all__ = ('async_generator', 'isasyncgenfunction', 'isasyncgeneratorfunction')


class _AsyncGeneratorWrapper:
    __slots__ = 'coroutine'

    def __init__(self, coroutine: Coroutine) -> None:
        self.coroutine = coroutine

    if sys.version_info < (3, 5, 2):
        async def __aiter__(self):  # pragma: no cover
            return self
    else:
        def __aiter__(self):
            return self

    async def __anext__(self):
        value = await work_coroutine(self.coroutine)
        if value is not None:
            return value.value
        else:
            raise StopAsyncIteration


def async_generator(func: Callable[..., Coroutine]) -> Callable[..., AsyncIterator]:
    """
    Transform a coroutine function into something that works with ``async for``.

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

    .. note:: This decorator has been obsoleted by Python 3.6. When targeting Python 3.6 or above,
      remove the decorator and use the ``yield`` statement in place of ``await yield_async(...)``.

    :param func: a coroutine function
    :return: a callable that returns an async iterator

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return _AsyncGeneratorWrapper(func(*args, **kwargs))

    assert iscoroutinefunction(func), '"func" must be a coroutine function'
    wrapper._is_async_generator = True
    return wrapper


def isasyncgenfunction(obj) -> bool:
    """Return ``True`` if the given object is an asynchronous generator function."""
    if hasattr(inspect, 'isasyncgenfunction') and inspect.isasyncgenfunction(obj):
        return True

    return isfunction(obj) and getattr(obj, '_is_async_generator', False)


def isasyncgeneratorfunction(obj) -> bool:
    warn('This function has been renamed to "isasyncgenfunction"', DeprecationWarning)
    return isasyncgenfunction(obj)
