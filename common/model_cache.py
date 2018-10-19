
from django.db import models
from django.core.cache import cache
from django.dispatch import Signal

DOMAIN_CACHE_PREFIX = 'model1'

clear_cache_sig = Signal(providing_args=['key'])


def cache_key(model, pk):
    return ("%s-%s-%s" % (DOMAIN_CACHE_PREFIX, model._meta.db_table, pk)).replace(" ", "")


class CachedQuerySet(models.QuerySet):

    def get(self, *args, **kwargs):
        model_key = None
        ck = self.model.CACHE_KEY
        if ck in kwargs:
            uid = kwargs[ck]
            model_key = cache_key(self.model, uid)
            model = cache.get(model_key)
            if model is not None:
                if model is 0:
                    model = None
                return model

        try:
            model = super(CachedQuerySet, self).get(*args, **kwargs)
        except self.model.DoesNotExist:
            model = None

        if model_key:
            if model is None:
                model = 0
            else:
                model.before_cache_set()
            cache.set(model_key, model, self.model.CACHE_EXPIRE)

        return model

    def get_or_create(self, **kwargs):
        defaults = kwargs.pop('defaults', {})
        v = self.get(**kwargs)
        if not v:
            lookup, params = self._extract_model_params(defaults, **kwargs)
            # The get() needs to be targeted at the write database in order
            # to avoid potential transaction consistency problems.
            self._for_write = True
            return self._create_object_from_params(lookup, params)
        return v, False


class CachedManager(models.Manager.from_queryset(CachedQuerySet)):

    # change name to fix m2m result error
    # should explicit call cached_all to use cache
    def cached_all(self):
        queryset_key = None
        qs = self.model.CACHE_QUERYSET
        if qs:
            queryset_key = cache_key(self.model, 'all')
            queryset = cache.get(queryset_key)
            if queryset is not None:
                return queryset

        if isinstance(qs, dict):
            queryset = super(CachedManager, self).filter(**qs)
        else:
            queryset = super(CachedManager, self).all()

        for item in queryset:
            item.before_cache_set()
        cache.set(queryset_key, list(queryset), self.model.CACHE_EXPIRE)
        return queryset

    def cached_filter(self, v):
        queryset_key = cache_key(self.model, 'filter_'+str(v))
        queryset = cache.get(queryset_key)
        if queryset is not None:
            return queryset

        kv = {self.model.FILTER_KEY: v}
        queryset = super(CachedManager, self).filter(**kv)

        for item in queryset:
            item.before_cache_set()

        cache.set(queryset_key, list(queryset), self.model.CACHE_EXPIRE)

        return queryset


class CachedModel(models.Model):

    objects = CachedManager()
    CACHE_KEY = 'pk'
    CACHE_EXPIRE = None
    CACHE_QUERYSET = False
    FILTER_KEY = None

    class Meta:
        abstract = True

    # hooker to set extra attribute to cache
    def before_cache_set(self):
        pass

    def delete_cache(self):
        model_key = cache_key(self, getattr(self, self.CACHE_KEY))
        cache.delete(model_key)
        if self.CACHE_QUERYSET:
            queryset_key = cache_key(self, 'all')
            cache.delete(queryset_key)

        if self.FILTER_KEY:
            v = getattr(self, self.FILTER_KEY)
            queryset_key = cache_key(self, 'filter_'+str(v))
            print("delete filter key %s" % queryset_key)
            cache.delete(queryset_key)
