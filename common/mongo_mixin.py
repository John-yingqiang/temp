from django.utils.functional import cached_property
from .mongo import mongodb, mongo_client
import re
from functools import reduce
import operator


def chained(v):
    if isinstance(v, dict):
        v = JsonDict(v)
    elif isinstance(v, list):
        v = JsonList(v)
    elif v is None:
        v = Empty()
    return v


operators = {
    'exact': lambda a, b: a == b,
    'iexact': lambda a, b: str(a).upper() == str(b).upper(),
    'in': lambda a, b: a in b,
    'contains': lambda a, b: b in a,
    'gt': lambda a, b: a > b,
    'lt': lambda a, b: a < b,
    'gte': lambda a, b: a >= b,
    'lte': lambda a, b: a <= b,
    'startswith': lambda a, b: a.startswith(b),
    'endswith': lambda a, b: a.endswith(b),
}


def get_item_value(item, k):
    if isinstance(item, dict):
        return item.get(k)
    if isinstance(item, list):
        r = re.match('i(\d+)', k)
        k = int(r.group(1))
    else:
        return item
    try:
        return item[k]
    except (KeyError, IndexError):
        return None


class Empty(object):

    def __init__(self, v=None):
        pass

    def __getattr__(self, attr):
        return self.__class__()

    def __getitem__(self, item):
        return self.__class__()

    def __call__(self, *args, **kwargs):
        return self.__class__()

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __le__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __int__(self):
        return 0

    def __str__(self):
        return ''

    def __bool__(self):
        return False

    def __len__(self):
        return 0

    def __contains__(self, item):
        return False



class JsonMixin(object):

    def len(self):
        return len(self)

    def max(self,):
        return max(self)

    def min(self,):
        return max(self)

    def all(self,):
        return all(self)

    def any(self):
        return any(self)

    def join(self, s=''):
        return s.join(self)


class JsonDict(dict, JsonMixin):

    def sum(self):
        return sum(self.values())

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __getitem__(self, key):
        try:
            v = super().__getitem__(key)
            return chained(v)
        except KeyError:
            return Empty()


class JsonList(list, JsonMixin):

    def sum(self, start=0, end=None):
        end = end or len(self)
        return sum(self[start:end])

    def sub(self, key):
        sub = [a[key] for a in self]
        return self.__class__(sub)

    def issuperset(self, s):
        return set(self) >= set(s)

    def set(self):
        return set(self)

    def issubset(self, s):
        return set(self) <= set(s)

    def flat(self):
        return self.__class__(reduce(operator.concat, self))

    def filter(self, **kwargs):
        def func(item):
            for k, v in kwargs.items():
                r = re.match('(\w+)__(\w+)', k)
                if r:
                    k = r.group(1)
                    op = r.group(2)
                else:
                    op = 'exact'
                if not operators[op](get_item_value(item, k), v):
                    return False
            return True
        a = [x for x in self if func(x)]
        return chained(a)

    def __getattr__(self, attr):
        r = re.match('i(\d+)', attr)
        if r:
            index = int(r.group(1))
            try:
                v = self[index]
                return chained(v)
            except IndexError:
                return Empty()
        else:
            sub = [a.get(attr) for a in self]
            return self.__class__(sub)


class MongoMixin(object):

    db = None
    mongo_table = None

    @cached_property
    def mongo_data(self):
        db = mongo_client[self.db] if self.db else mongodb
        return db[self.mongo_table].find_one({'_id': self.id}) or {}

    def get_mongo_data(self, key):
        v = self.mongo_data.get(key)
        return chained(v)

    def __getattr__(self, key):
        value = self.get_mongo_data(key)
        setattr(self, key, value)
        return value

    def __getitem__(self, key):
        value = self.get_mongo_data(key)
        setattr(self, key, value)
        return value
