from asyncio_extras import isasyncgenfunction


def test_isasyncgenfunction():
    async def asyncgenfunc():
        yield 1

    assert isasyncgenfunction(asyncgenfunc)
