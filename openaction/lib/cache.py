
from django.conf import settings

import redis, pickle

conn_params = {}

if settings.REDIS_SERVER_ADDR: conn_params['host'] = settings.REDIS_SERVER_ADDR
if settings.REDIS_SERVER_PORT: conn_params['port'] = settings.REDIS_SERVER_PORT, 
if settings.REDIS_DATABASE   : conn_params['db']   = settings.REDIS_DATABASE, 
		
rc = redis.Redis(**conn_params)
	

class Store(object):

    @classmethod
    def get(cls, key):
        rv = rc.get(key)
        if rv is not None:
            rv = pickle.loads(rv)
        return rv

    @classmethod
    def set(cls, key, value):

        pickled_value = pickle.dumps(value)
        return rc.set(key, pickled_value)

