import time
import functools


def delay_seconds(seconds):
  def decorator_delay(func):
    @functools.wraps(func)
    def wrapper_delay(*args, **kwargs):
      time.sleep(seconds)
      return func(*args, **kwargs)
    return wrapper_delay
  return decorator_delay