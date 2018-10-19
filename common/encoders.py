from rest_framework.utils.encoders import JSONEncoder
from bson import ObjectId
from datetime import datetime, date


class MongoJsonEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.decode()
        return super(MongoJsonEncoder, self).default(obj)
