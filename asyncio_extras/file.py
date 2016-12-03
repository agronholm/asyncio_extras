import sys
from concurrent.futures import Executor
from io import IOBase  # noqa
from pathlib import Path
from typing import Union, Optional

from async_generator import async_generator, yield_

from asyncio_extras.threads import threadpool, call_in_executor

__all__ = ('AsyncFileWrapper', 'open_async')


class AsyncFileWrapper:
    """
    Wraps certain file I/O operations so they're guaranteed to run in a thread pool.

    The wrapped methods work like coroutines when called in the event loop thread, but when called
    in any other thread, they work just like the methods of the ``file`` type.

    This class supports use as an asynchronous context manager.

    The wrapped methods are:

    * ``flush()``
    * ``read()``
    * ``readline()``
    * ``readlines()``
    * ``seek()``
    * ``truncate()``
    * ``write()``
    * ``writelines()``
    """

    __slots__ = ('_open_args', '_open_kwargs', '_executor', '_raw_file', 'flush', 'read',
                 'readline', 'readlines', 'seek', 'truncate', 'write', 'writelines')

    def __init__(self, path: str, args: tuple, kwargs: dict, executor: Optional[Executor]) -> None:
        self._open_args = (path,) + args
        self._open_kwargs = kwargs
        self._executor = executor
        self._raw_file = None  # type: IOBase

    def __getattr__(self, name):
        return getattr(self._raw_file, name)

    def __await__(self):
        if self._raw_file is None:
            self._raw_file = yield from call_in_executor(
                open, *self._open_args, executor=self._executor, **self._open_kwargs)
            self.flush = threadpool(self._executor)(self._raw_file.flush)
            self.read = threadpool(self._executor)(self._raw_file.read)
            self.readline = threadpool(self._executor)(self._raw_file.readline)
            self.readlines = threadpool(self._executor)(self._raw_file.readlines)
            self.seek = threadpool(self._executor)(self._raw_file.seek)
            self.truncate = threadpool(self._executor)(self._raw_file.truncate)
            self.write = threadpool(self._executor)(self._raw_file.write)
            self.writelines = threadpool(self._executor)(self._raw_file.writelines)

        return self

    def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._raw_file.close()

    if sys.version_info < (3, 5, 2):
        async def __aiter__(self):  # pragma: no cover
            return self
    else:
        def __aiter__(self):
            return self

    async def __anext__(self):
        if self._raw_file is None:
            await self

        line = await self.readline()
        if line:
            return line
        else:
            raise StopAsyncIteration

    @async_generator
    async def async_readchunks(self, size: int):
        """
        Read data from the file in chunks.

        :param size: the maximum number of bytes or characters to read at once
        :return: an asynchronous iterator yielding bytes or strings

        """
        while True:
            data = await self.read(size)
            if data:
                await yield_(data)
            else:
                return


def open_async(file: Union[str, Path], *args, executor: Executor = None,
               **kwargs) -> AsyncFileWrapper:
    """
    Open a file and wrap it in an :class:`~AsyncFileWrapper`.

    Example::

        async def read_file_contents(path: str) -> bytes:
            async with open_async(path, 'rb') as f:
                return await f.read()

    The file wrapper can also be asynchronously iterated line by line::

        async def read_file_lines(path: str):
            async for line in open_async(path):
                print(line)

    :param file: the file path to open
    :param args: positional arguments to :func:`open`
    :param executor: the ``executor`` argument to :class:`~AsyncFileWrapper`
    :param kwargs: keyword arguments to :func:`open`
    :return: the wrapped file object

    """
    return AsyncFileWrapper(str(file), args, kwargs, executor)
