from .models import BaseMatch, CachedTarget, Matcher
from functools import reduce


def match_all(prop, matches):
    if not matches:
        return True
    for m in matches:
        result = m.match_with(prop)

        if m.next is BaseMatch.END:
            return result

        if result and m.next is BaseMatch.OR:
            return True
        if not result and m.next is BaseMatch.AND:
            return False

    return False


class MatchException(Exception):

    def __init__(self, msg):
        self.message = msg


def match_first(targets, data, raise_exception=True):
    for v in targets:
        if match_all(data, v.matches):
            return v

    if raise_exception:
        raise MatchException("target not found for %s in %s" % (data, targets))


def match_and_filter(targets, data):
    results = filter(lambda t: match_all(data, t.matches), targets)
    return results


def match_and_map(targets, data, mapper):
    results = filter(lambda t: match_all(data, t.matches), targets)
    results = map(mapper, results)
    return results


def match_and_map_reduce(targets, data, mapper, reducer, initial=None):
    results = filter(lambda t: match_all(data, t.matches), targets)
    results = map(mapper, results)
    results = reduce(reducer, results, initial)
    return results


class SingleMatchMixin(object):

    next = BaseMatch.END

    @property
    def matches(self):
        return [self]

    def match_with(self):
        raise NotImplementedError()
