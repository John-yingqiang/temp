from django.shortcuts import _get_queryset
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
import re
import uuid


def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), a MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
    except MultipleObjectsReturned:
        return queryset.filter(*args, **kwargs).first()


def get_config(key, default=None):
    """
    Get settings from django.conf if exists,
    return default value otherwise

    example:

    ADMIN_EMAIL = get_config('ADMIN_EMAIL', 'default@email.com')
    """
    return getattr(settings, key, default)


def get_object_or_this(model, this=None, *args, **kwargs):
    """
    Uses get() to return an object or the value of <this> argument
    if object does not exist.

    If the <this> argument if not provided None would be returned.
    <model> can be either a QuerySet instance or a class.
    """

    return get_object_or_none(model, *args, **kwargs) or this


def parse_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default


def parse_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def get_match_or_none(reg, value):
    m = re.match(reg, value)
    return m and m.group(0)


def ip_to_string(ip):
    if ip:
        return '.'.join([str(ip >> 24), str((ip >> 16) & 0xff), str((ip >> 8) & 0xff), str(ip & 0xff)])
    else:
        return None


def string_to_ip(string):
    segments = string.split('.')
    try:
        return (int(segments[0]) << 24) + (int(segments[1]) << 16) + (int(segments[2]) << 8) + (int(segments[3]))
    except ValueError:
        pass
    except IndexError:
        pass
    return 0


def merge_dict(a, b, path=[]):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    merge_dict(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
    return a


def remove_none_ascii(text):
    return ''.join(i for i in text if ord(i) < 128)


def float_delete_tail(value):
    """
    :param value: float
    :return: 
    """
    value_int = int(value)
    if value_int == value:
        return value_int
    return value


class DictEnum(object):
    def __init__(self, kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        raise AttributeError()


def uuid_2_ts(u):
    a = uuid.UUID(u)
    ts = (a.time - 0x01b21dd213814000) * 100 / 1e9
    return ts
