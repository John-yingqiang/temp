
from django.utils.functional import SimpleLazyObject
from pymongo import MongoClient, ReturnDocument
from django.conf import settings

mongo_client = SimpleLazyObject(lambda: MongoClient(settings.MONGO_SERVER))
mongodb = SimpleLazyObject(lambda: mongo_client[settings.MONGO_DB])

from bson import ObjectId, errors
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer
from .renderers import MongoJsonRenderer
from django.dispatch import Signal
from .functions import parse_int


post_save = Signal(providing_args=['instance', 'created'])
post_delete = Signal(providing_args=['instance'])


def get_object_id(_id, raise_exception=True):
    try:
        return ObjectId(_id)
    except errors.InvalidId as e:
        if raise_exception:
            raise ValidationError({"_id": str(e)})
        else:
            return parse_int(_id) or _id


def get_object_data(data):
    if not isinstance(data, dict):
        raise ValidationError({"data": "Invalid data"})
    return data


class MongoViewSet(viewsets.ModelViewSet):

    renderer_classes = (MongoJsonRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.Serializer
    queryset = []
    model = None
    strict_bson = True
    collection = None

    def get_table(self):
        return mongodb[self.collection]

    def before_update(self, request, data, partial):
        try:
            data.pop('_id')
        except KeyError:
            pass

    def before_create(self, request, data):
        pass

    def list(self, request, *args, **kwargs):
        table = self.get_table()
        data = list(table.find())
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        _id = get_object_id(self.kwargs['pk'], self.strict_bson)
        table = self.get_table()
        data = table.find_one({'_id': _id})
        if not data:
            raise NotFound()
        return Response(data)

    def create(self, request):
        data = get_object_data(request.data)
        self.before_create(request, data)
        table = self.get_table()
        table.insert_one(data)
        if self.model:
            post_save.send(self.model, instance=data, created=True)
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        _id = get_object_id(self.kwargs['pk'], self.strict_bson)
        data = get_object_data(request.data)
        self.before_update(request, data, partial)
        table = self.get_table()
        if partial:
            data = table.find_one_and_update({'_id': _id}, {'$set': data}, return_document=ReturnDocument.AFTER)
        else:
            data = table.find_one_and_replace({'_id': _id}, data, return_document=ReturnDocument.AFTER)
        if not data:
            raise NotFound()
        if self.model:
            post_save.send(self.model, instance=data, created=False)
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        _id = get_object_id(self.kwargs['pk'], self.strict_bson)
        table = self.get_table()
        data = table.find_one_and_delete({'_id': _id})
        print("delete:", data)
        if self.model and data:
            post_delete.send(self.model, instance=data)
        return Response(status=status.HTTP_204_NO_CONTENT)
