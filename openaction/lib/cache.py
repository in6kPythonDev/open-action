# Copyright (C) 2012 Luca Ferroni <http://www.befair.it>
# License GNU Affero General Public License


# This file has been initially taken from SANET by Laboratori Guglielmo Marconi <http://www.labs.it>
# Main parts of the (small) code have been rewritten

from django.conf import settings

import redis, pickle

conn_params = {}

if settings.REDIS_SERVER_ADDR: conn_params['host'] = settings.REDIS_SERVER_ADDR
if settings.REDIS_SERVER_PORT: conn_params['port'] = settings.REDIS_SERVER_PORT, 
if settings.REDIS_DATABASE   : conn_params['db']   = settings.REDIS_DATABASE, 
		
rc = redis.Redis(**conn_params)
	

class Store(object):

    key_prefix = ''

    @classmethod
    def get(cls, key):
        key = cls.key_prefix+key
        rv = rc.get(key)
        if rv is not None:
            rv = pickle.loads(rv)
        return rv

    @classmethod
    def set(cls, key, value):
        key = cls.key_prefix+key
        pickled_value = pickle.dumps(value)
        return rc.set(key, pickled_value)

    @classmethod
    def clean(cls):
        for k in rc.keys(cls.key_prefix+'*'):
            rc.delete(k)

