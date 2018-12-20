# Common things for the raspberry pi section of the christmas tree

import json
import redis

def read_settings(filename):
    with open(filename) as f:
        return json.load(f)

def open_redis(settings):
    password = settings['redis-password'] if settings['redis-auth'] else None
    return redis.StrictRedis(host=settings['redis-hostname'], port=settings['redis-port'], password=password)

