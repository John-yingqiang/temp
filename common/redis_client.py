
import os
from redis import StrictRedis

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PWD = os.environ['REDIS_PWD']
REDIS_DB = os.environ['REDIS_DB']

rc = StrictRedis(host=REDIS_HOST, password=REDIS_PWD, db=REDIS_DB)
