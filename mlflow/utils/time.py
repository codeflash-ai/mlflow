import datetime
import time
from functools import lru_cache


def get_current_time_millis():
    """
    Returns the time in milliseconds since the epoch as an integer number.
    """
    return int(time.time() * 1000)


def conv_longdate_to_str(longdate, local_tz=True):
    # Avoid division in hot loop: use integer division if possible, else use float
    timestamp = longdate / 1000.0
    date_time = datetime.datetime.fromtimestamp(timestamp)
    str_long_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
    if local_tz:
        tzinfo = _get_local_tzinfo()
        if tzinfo:
            # tzinfo.tzname() is potentially costly; only call if tzinfo exists
            str_long_date = f"{str_long_date} {tzinfo.tzname(date_time)}"
    return str_long_date


@lru_cache(maxsize=1)
def _get_local_tzinfo():
    # Caches local tzinfo instance for performance (assumes it doesn't change)
    return datetime.datetime.now().astimezone().tzinfo


class Timer:
    """
    Measures elapsed time.

    .. code-block:: python

        from mlflow.utils.time import Timer

        with Timer() as t:
            ...

        print(f"Elapsed time: {t:.2f} seconds")
    """

    def __init__(self):
        self.elapsed = 0.0

    def __enter__(self):
        self.elapsed = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = time.perf_counter() - self.elapsed

    def __format__(self, format_spec: str) -> str:
        return self.elapsed.__format__(format_spec)

    def __repr__(self) -> str:
        return self.elapsed.__repr__()

    def __str__(self) -> str:
        return self.elapsed.__str__()
