import asyncio

import pytest

from asyncio_extras import async_contextmanager


@pytest.mark.asyncio
async def test_async_contextmanager():
    @async_contextmanager
    async def dummycontext(value):
        yield value

    async with dummycontext(2) as value:
        assert value == 2


@pytest.mark.asyncio
async def test_async_contextmanager_two_awaits():
    @async_contextmanager
    async def dummycontext(value):
        await asyncio.sleep(0.1)
        yield value
        await asyncio.sleep(0.1)

    async with dummycontext(2) as value:
        assert value == 2


@pytest.mark.asyncio
async def test_async_contextmanager_exception():
    @async_contextmanager
    async def dummycontext(value):
        nonlocal exception
        try:
            yield value
        except Exception as e:
            exception = e

    exception = None
    async with dummycontext(2):
        raise Exception('foo')

    assert str(exception) == 'foo'


@pytest.mark.asyncio
async def test_async_contextmanager_exception_passthrough():
    @async_contextmanager
    async def dummycontext():
        yield

    with pytest.raises(Exception) as exception:
        async with dummycontext():
            raise Exception('foo')

    assert exception.match('^foo$')


@pytest.mark.asyncio
async def test_async_contextmanager_extra_yield():
    @async_contextmanager
    async def dummycontext(value):
        yield value
        yield 3

    with pytest.raises(RuntimeError) as exc:
        async with dummycontext(2) as value:
            assert value == 2

    assert str(exc.value) == "async generator didn't stop"


@pytest.mark.asyncio
async def test_return_after_yield():
    @async_contextmanager
    async def dummycontext(value):
        try:
            yield value
        except RuntimeError:
            return

    async with dummycontext(2) as value:
        assert value == 2
        raise RuntimeError
