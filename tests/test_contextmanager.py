import asyncio

import pytest

from asyncio_extras import yield_async, async_contextmanager


@pytest.mark.asyncio
async def test_async_contextmanager():
    @async_contextmanager
    async def dummycontext(value):
        await yield_async(value)

    async with dummycontext(2) as value:
        assert value == 2


@pytest.mark.asyncio
async def test_async_contextmanager_three_awaits():
    @async_contextmanager
    async def dummycontext(value):
        await asyncio.sleep(0.1)
        await yield_async(value)
        await asyncio.sleep(0.1)

    async with dummycontext(2) as value:
        assert value == 2


@pytest.mark.asyncio
async def test_async_contextmanager_no_yield():
    @async_contextmanager
    async def dummycontext():
        pass

    with pytest.raises(RuntimeError) as exc:
        async with dummycontext():
            pass

    assert str(exc.value) == 'coroutine finished without yielding a value'


@pytest.mark.asyncio
async def test_async_contextmanager_extra_yield():
    @async_contextmanager
    async def dummycontext(value):
        await yield_async(value)
        await yield_async(3)

    with pytest.raises(RuntimeError) as exc:
        async with dummycontext(2) as value:
            assert value == 2

    assert str(exc.value) == 'coroutine yielded a value in the exit phase: 3'
