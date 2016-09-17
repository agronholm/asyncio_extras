Version history
===============

This library adheres to `Semantic Versioning <http://semver.org/>`_.

**1.2.0**

- Renamed the ``isasyncgeneratorfunction`` function to ``isasyncgenfunction`` to match the new
  function in the ``inspect`` module in Python 3.6 (the old name still works though)
- Updated ``isasyncgenfunction`` to recognize native asynchronous generator functions in Python 3.6
  and above

**1.1.3** (2016-09-05)

- Fixed error when throwing an exception into an asynchronous generator when using asyncio's debug
  mode

**1.1.2** (2016-08-14)

- Fixed concurrency issue with ``async with threadpool()`` when more than one coroutine from the
  same coroutine function is being run

**1.1.1** (2016-04-14)

- Import ``call_async`` to the ``asyncio_extras`` package namespace (this was missing from the
  1.1.0 release)

**1.1.0** (2016-04-04)

- Added the ``asyncio_extras.threads.call_async`` function

**1.0.0** (2016-04-08)

- Initial release
