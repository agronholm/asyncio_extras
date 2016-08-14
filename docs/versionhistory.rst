Version history
===============

This library adheres to `Semantic Versioning <http://semver.org/>`_.

**1.1.2**

- Fixed concurrency issue with ``async with threadpool()`` when more than one coroutine from the
  same coroutine function is being run

**1.1.1**

- Import ``call_async`` to the ``asyncio_extras`` package namespace (this was missing from the
  1.1.0 release)

**1.1.0**

- Added the ``asyncio_extras.threads.call_async`` function

**1.0.0**

Initial release.
