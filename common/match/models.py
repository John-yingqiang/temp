from django.db import models
from ..model_cache import CachedModel
from django.utils.functional import cached_property
import re
import traceback
import json
from general.email import send_email
from django.core.exceptions import ValidationError


def str_bool(v):
    v = v.lower()
    if v in ['true', 'yes', '1']:
        return True
    if v in ['false', 'no', '0', '']:
        return False
    raise ValueError("cannot convert %s to boolean " % v)


def sanitize_script(text):
    return re.sub('\s+', ' ', text).strip()


def eval_script(context, script):
    script = sanitize_script(script)
    ret = eval(script, {'re': re}, context)
    return ret


class BaseMatch(models.Model):

    END = 0
    OR = 1
    AND = 2

    next_choices = [
        (END, '结束'),
        (OR, '或者'),
        (AND, '而且'),
    ]

    is_array = models.BooleanField(default=False)
    value = models.CharField(max_length=100, verbose_name='值', blank=True)
    next = models.SmallIntegerField(default=OR, choices=next_choices)

    @property
    def key(self):
        raise NotImplementedError()

    @property
    def op(self):
        raise NotImplementedError()

    def value_b(self, func):
        v = self.value
        if self.is_array:
            vs = sanitize_script(v).split(' ')
            vs = [func(a) for a in vs]
        else:
            vs = func(v)
        return vs

    def match_with(self, d):
        try:
            keys = self.key.split('.')
            attr = d
            for k in keys:
                attr = attr[k]

            if attr is None:
                return False

            func = type(attr)
            if func is bool:
                func = str_bool
            b = self.value_b(func)
            c = {'a': attr, 'b': b}
            result = eval_script(c, self.op)
            # print(self.key, attr, self.op, b, result)
        except:
            s = self.op
            tb = traceback.format_exc()
            print(s + tb)
            send_email(s, tb)
            result = False
        return result

    class Meta:
        abstract = True


class CachedTarget(CachedModel):

    CACHE_QUERYSET = True

    uid = models.CharField(max_length=16, unique=True)
    index = models.PositiveIntegerField(default=0, db_index=True)
    desc = models.CharField(max_length=32, blank=True)

    @cached_property
    def matches(self):
        return list(self.match_set.all())

    def before_cache_set(self):
        self.matches

    class Meta:
        ordering = ['-index']
        abstract = True

    def __str__(self):
        return self.uid


class Matcher(BaseMatch):

    target = None
    attribute = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)

    @property
    def key(self):
        return self.attribute

    @property
    def op(self):
        return self.operation

    class Meta:
        abstract = True
