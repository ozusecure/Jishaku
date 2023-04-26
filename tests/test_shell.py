# -*- coding: utf-8 -*-

"""
jishaku.shell test
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2021 Devon (Gorialis) R
:license: MIT, see LICENSE for more details.

"""

import asyncio
import sys

import pytest

from jishaku.shell import ShellReader


@pytest.mark.asyncio
async def test_reader_basic():
    return_data: list[str] = []

    with ShellReader("echo hi") as reader:
        async for result in reader:
            return_data.append(result)

    assert len(return_data) == 1
    assert return_data[0] == "hi"

    with pytest.raises(asyncio.TimeoutError):
        with ShellReader("sleep 2", timeout=1) as reader:
            async for result in reader:
                pass

    await asyncio.sleep(0.5)  # Ensure ShellReader.executor_wrapper completes


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Tests with Linux-only sh syntax"
)
@pytest.mark.asyncio
async def test_linux():
    return_data: list[str] = []

    with ShellReader(">&2 echo oops") as reader:
        async for result in reader:
            return_data.append(result)

    assert len(return_data) == 1
    assert return_data[0] == "[stderr] oops"

    return_data = []

    with ShellReader("echo one && echo two") as reader:
        async for result in reader:
            return_data.append(result)

    assert len(return_data) == 2
    assert return_data[0] == "one"
    assert return_data[1] == "two"


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Tests with Windows-only cmd syntax"
)
@pytest.mark.asyncio
async def test_windows():
    return_data: list[str] = []

    with ShellReader("cmd /c \"echo one && echo two && echo three 1>&2\"") as reader:
        async for result in reader:
            return_data.append(result)

    assert len(return_data) == 3
    return_data = [x.strip() for x in return_data]

    assert "one" in return_data
    assert "two" in return_data
    assert "[stderr] three" in return_data
