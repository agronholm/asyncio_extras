import pytest

from asyncio_extras.asyncyield import yield_async
from asyncio_extras.generator import async_generator, isasyncgeneratorfunction


@pytest.mark.asyncio
async def test_yield():
    """Test that values yielded by yield_async() end up in the consumer."""
    @async_generator
    async def dummygenerator(start):
        await yield_async(start)
        await yield_async(start + 1)
        await yield_async(start + 2)

    values = []
    async for value in dummygenerator(2):
        values.append(value)

    assert values == [2, 3, 4]


@pytest.mark.asyncio
async def test_exception():
    """Test that an exception raised directly in the async generator is properly propagated."""
    @async_generator
    async def dummygenerator(start):
        await yield_async(start)
        raise ValueError('foo')

    values = []
    with pytest.raises(ValueError) as exc:
        async for value in dummygenerator(2):
            values.append(value)

    assert values == [2]
    assert str(exc.value) == 'foo'


@pytest.mark.asyncio
async def test_awaitable_exception(event_loop):
    """
    Test that an exception raised in something awaited by the async generator is sent back to
    the generator.

    """
    def raise_error():
        raise ValueError('foo')

    @async_generator
    async def dummygenerator():
        try:
            await event_loop.run_in_executor(None, raise_error)
        except ValueError as e:
            await yield_async(e)

    values = []
    async for value in dummygenerator():
        values.append(value)

    assert str(values[0]) == 'foo'


def test_isasyncgeneratorfunction():
    async def normalfunc():
        pass

    assert not isasyncgeneratorfunction(normalfunc)
    assert isasyncgeneratorfunction(async_generator(normalfunc))
