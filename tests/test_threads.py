import asyncio
import threading
from asyncio.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from threading import current_thread, main_thread

import pytest
import time

from asyncio_extras import threadpool, call_in_executor
from asyncio_extras.threads import call_async


class TestThreadpool:
    @pytest.mark.parametrize('already_in_thread', [False, True])
    @pytest.mark.asyncio
    async def test_threadpool_decorator_noargs(self, event_loop, already_in_thread):
        """Test that threadpool() without arguments works as a decorator."""
        @threadpool
        def func(x, y):
            nonlocal func_thread
            func_thread = threading.current_thread()
            return x + y

        event_loop_thread = threading.current_thread()
        func_thread = None
        callback = (event_loop.run_in_executor(None, func, 1, 2) if already_in_thread else
                    func(1, 2))
        assert await callback == 3
        assert func_thread is not event_loop_thread

    @pytest.mark.parametrize('executor', [None, ThreadPoolExecutor(1)])
    @pytest.mark.asyncio
    async def test_threadpool_decorator(self, executor):
        """Test that threadpool() with an argument works as a decorator."""
        @threadpool(executor)
        def func(x, y):
            nonlocal func_thread
            func_thread = threading.current_thread()
            return x + y

        event_loop_thread = threading.current_thread()
        func_thread = None
        assert await func(1, 2) == 3
        assert func_thread is not event_loop_thread

    @pytest.mark.asyncio
    async def test_threadpool_contextmanager(self):
        """Test that threadpool() with an argument works as a context manager."""
        event_loop_thread = threading.current_thread()

        async with threadpool():
            func_thread = threading.current_thread()

        assert threading.current_thread() is event_loop_thread
        assert func_thread is not event_loop_thread

    @pytest.mark.asyncio
    async def test_threadpool_contextmanager_exception(self):
        """Test that an exception raised from a threadpool block is properly propagated."""
        event_loop_thread = threading.current_thread()

        with pytest.raises(ValueError) as exc:
            async with threadpool():
                raise ValueError('foo')

        assert threading.current_thread() is event_loop_thread
        assert str(exc.value) == 'foo'

    @pytest.mark.asyncio
    async def test_threadpool_await_in_thread(self):
        """Test that attempting to await in a thread results in a RuntimeError."""
        future = Future()

        with pytest.raises(RuntimeError) as exc:
            async with threadpool():
                await future

        assert str(exc.value) == 'attempted to "await" in a worker thread'

    @pytest.mark.asyncio
    async def test_threadpool_multiple_coroutine(self):
        """
        Test that "async with threadpool()" works when there are multiple coroutine objects present
        for the same coroutine function.

        """
        async def sleeper():
            await asyncio.sleep(0.2)
            async with threadpool():
                time.sleep(0.3)

        coros = [sleeper() for _ in range(10)]
        await asyncio.gather(*coros)


@pytest.mark.parametrize('executor', [None, ThreadPoolExecutor(1)])
@pytest.mark.asyncio
async def test_call_in_executor(executor):
    """Test that call_in_thread actually runs the target in a worker thread."""
    assert not await call_in_executor(lambda: current_thread() is main_thread(),
                                      executor=executor)


class TestCallAsync:
    @pytest.mark.asyncio
    async def test_call_async_plain(self, event_loop):
        def runs_in_event_loop(worker_thread, x, y):
            assert current_thread() is not worker_thread
            return x + y

        def runs_in_worker_thread():
            worker_thread = current_thread()
            return call_async(event_loop, runs_in_event_loop, worker_thread, 1, y=2)

        assert await event_loop.run_in_executor(None, runs_in_worker_thread) == 3

    @pytest.mark.asyncio
    async def test_call_async_coroutine(self, event_loop):
        async def runs_in_event_loop(worker_thread, x, y):
            assert current_thread() is not worker_thread
            await asyncio.sleep(0.2)
            return x + y

        def runs_in_worker_thread():
            worker_thread = current_thread()
            return call_async(event_loop, runs_in_event_loop, worker_thread, 1, y=2)

        assert await event_loop.run_in_executor(None, runs_in_worker_thread) == 3

    @pytest.mark.asyncio
    async def test_call_async_exception(self, event_loop):
        def runs_in_event_loop():
            raise ValueError('foo')

        with pytest.raises(ValueError) as exc:
            await event_loop.run_in_executor(None, call_async, event_loop, runs_in_event_loop)

        assert str(exc.value) == 'foo'
