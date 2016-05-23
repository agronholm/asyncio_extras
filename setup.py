from pathlib import Path

from setuptools import setup

setup(
    name='asyncio_extras',
    use_scm_version={
        'version_scheme': 'post-release',
        'local_scheme': 'dirty-tag'
    },
    description='Asynchronous generators, context managers and more for asyncio',
    long_description=Path(__file__).with_name('README.rst').read_text('utf-8'),
    author='Alex Grönholm',
    author_email='alex.gronholm@nextday.fi',
    url='https://github.com/agronholm/asyncio_extras',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    license='MIT',
    zip_safe=False,
    packages=['asyncio_extras'],
    setup_requires=['setuptools_scm >= 1.7.0']
)
