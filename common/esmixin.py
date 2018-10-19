from django.utils.functional import cached_property
from .mongo_mixin import chained
import requests
import os

es_url = os.environ['ES_URL']
es_user = os.environ['ES_USER']
es_pwd = os.environ['ES_PWD']


def get_data(index, _id):
    url = "{0}/{1}/{1}/{2}".format(es_url, index, _id)
    r = requests.get(url, auth=(es_user, es_pwd))
    result = r.json()
    return result.get('_source')


class EsdataMixin(object):

    @cached_property
    def es_data(self):
        return get_data(self.es_index, self.id) or {}

    def get_es_data(self, key):
        v = self.es_data.get(key)
        return chained(v)

    def __getattr__(self, key):
        value = self.get_es_data(key)
        setattr(self, key, value)
        return value
