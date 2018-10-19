from redis.client import Lock
from .redis_client import rc


class OnlyOne(Exception):
    def __init__(self, name):
        self.message = "Someone already there for " + name


def only_one(name=None, timeout=30, blocking_timeout=None, silent_fail=False, release=False):

    blocking = blocking_timeout is not None

    def wrapper(task):
        def func(*args, **kwargs):

            key = name or task.__name__

            acquired = Lock(rc, key, timeout=timeout, blocking=blocking, blocking_timeout=blocking_timeout).acquire()
            if not acquired:
                if silent_fail:
                    return None
                else:
                    raise OnlyOne(key)
            try:
                task(*args, **kwargs)
            finally:
                if release:
                    rc.delete(key)

        return func

    return wrapper
