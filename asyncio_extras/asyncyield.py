from warnings import warn

from async_generator import yield_

__all__ = ('yield_async',)


def yield_async(value=None):
    """The equivalent of ``yield`` in an asynchronous context manager or asynchronous generator."""
    warn('This function has been deprecated in favor of async_generator.yield_',
         DeprecationWarning)
    return yield_(value)
