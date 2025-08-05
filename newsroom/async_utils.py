import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Coroutine, Optional, TypeVar

__all__ = [
    "run_async_to_sync",
]

T = TypeVar("T")


def run_async_to_sync(coroutine: Coroutine[Any, Any, T], timeout: Optional[float] = None) -> T:
    """
    Runs a coroutine synchronously and returns its result.

    This function ensures that a coroutine runs to completion in a blocking manner.
    It handles different scenarios such as running in the main thread or a separate thread,
    and whether an event loop is already running or not.

    Args:
        coroutine (Coroutine[Any, Any, T]): The coroutine to run.
        timeout (float): The maximum time in seconds to wait for the coroutine to complete.
                         Default to None (no limit).

    Returns:
        T: The result of the coroutine.

    Raises:
        TimeoutError: If the coroutine execution exceeds the specified timeout.
        RuntimeError: If the event loop in a non-main thread is closed.

    Considerations when using this function:
        - It does not enforce thread safety for the operations within the coroutine.
        - It's not responsible for ensuring that any shared state/resources accessed by the coroutine
          are properly synchronized.

    This implementation is adapted from a solution shared on Stack Overflow:
    https://stackoverflow.com/a/78911765/240364
    """
    try:
        loop = get_or_create_event_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    # if we're in the main thread
    if threading.current_thread() is threading.main_thread():
        if not loop.is_running():
            return loop.run_until_complete(coroutine)
        else:
            return run_coroutine_in_thread(coroutine, timeout)
    else:
        if loop.is_closed():
            raise RuntimeError("Event loop in the current thread is closed")
        return asyncio.run_coroutine_threadsafe(coroutine, loop).result(timeout=timeout)


def create_event_loop() -> asyncio.AbstractEventLoop:
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    return new_loop


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get the current event loop or create a new one if none is running.
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return create_event_loop()


def run_coroutine_in_thread(coroutine: Coroutine[Any, Any, T], timeout: Optional[float] = None) -> T:
    """
    Run a coroutine in a new thread if the current thread's event loop is already running.

    Args:
        coroutine (Coroutine[Any, Any, T]): The coroutine to run.
        timeout (float): The maximum time in seconds to wait for the coroutine to complete.
                         Default to None (no limit).

    Returns:
        T: The result of the coroutine.

    Raises:
        TimeoutError: If the coroutine execution exceeds the specified timeout.
    """

    def run_in_new_loop():
        new_loop = create_event_loop()
        try:
            return new_loop.run_until_complete(coroutine)
        finally:
            new_loop.close()

    with ThreadPoolExecutor() as pool:
        future = pool.submit(run_in_new_loop)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            future.cancel()
            raise TimeoutError("Coroutine execution exceeded the timeout")
