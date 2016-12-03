from collections.abc import Coroutine, AsyncIterator
from typing import Callable
from warnings import warn

from async_generator import (
    async_generator as async_generator_, isasyncgenfunction as isasyncgenfunction_)

__all__ = ('async_generator', 'isasyncgenfunction', 'isasyncgeneratorfunction')


def async_generator(func: Callable[..., Coroutine]) -> Callable[..., AsyncIterator]:
    warn('This function has been deprecated in favor of async_generator.async_generator',
         DeprecationWarning)
    return async_generator_(func)


def isasyncgenfunction(obj) -> bool:
    warn('This function has been deprecated in favor of async_generator.isasyncgenfunction',
         DeprecationWarning)
    return isasyncgenfunction_(obj)


isasyncgeneratorfunction = isasyncgenfunction
