'''Este modulo está destinado a contener las principales funciones de manejo de redis'''
import json
from datetime import datetime
from typing import List,Dict

import redis

from apps.utils.logger_util import get_logger
from apps.utils.redis.redis_singleton import redis_local_pool
from apps.utils.json_util import to_json,from_json
import time

redis_client = redis.StrictRedis(connection_pool=redis_local_pool)
logger = get_logger('redis_manager')

class RedisIsLockedException(Exception):

    def __init__(self):
        self.message = ('Redis bloqueado')

    def __str__(self):
        return self.message



def _is_locked():
    b = redis_client.get('asiscall_busy')
    return b == b'true'

def _put_lock():
    redis_client.set('asiscall_busy', 'true')

def _quit_lock():
    redis_client.set('asiscall_busy', 'false')

def lock_redis(func):
    '''Este decorador debe usarse en todas las funciones que llaman a redis,
    ya que es un lock del mismo. Si muchas pequeñas tareas se estan ejecutando,
    en especial en distintos servers, es posible que una se quiera escribir en
    el mismo lugar que la otra, ya que se manejan listas de redis, entonces es
    conveniente que no se lea redis si es que está bloqueado.'''
    def wrapper(*args, **kwargs):
        try:
            count = 0
            while(_is_locked()):
                count += 1
                if count > 100:
                    raise RedisIsLockedException()
                time.sleep(0.1)
            _put_lock()
            return func(*args, **kwargs)
        finally:
            _quit_lock()

    return wrapper

def push_multiple(redis_list: str, some_list: List,redis_key_function=None) -> None:
    for e in some_list:
        push_with_key(redis_list, e,redis_key_function)


@lock_redis
def push_with_key(redis_list: str, o,redis_key_function=None) -> None:
    k = build_key(o.__class__) if not redis_key_function else redis_key_function(o)
    redis_client.set(k, object_to_json(o))
    redis_client.lpush(redis_list, k)

@lock_redis
def push(redis_list: str, o) -> None:
    redis_client.lpush(redis_list, object_to_json(o))


@lock_redis
def pop(redis_list: str,return_class=dict):
    elem = redis_client.get(redis_client.lpop(redis_list))
    return _json_bytes_to_app_object(elem,return_class)


def list_count(redis_list: str) -> int:
    return redis_client.llen(redis_list)

def clear(list_name:str):
    redis_client.delete(list_name)

def build_key(some_class) -> str:
    return f"asiscall_{some_class.__name__}"

def object_to_json(some_object):
     return to_json(some_object)
    
def _json_bytes_to_app_object(s: bytes,some_class):
    return from_json(s,some_class)

def get_by_key(key:str,return_class):
    return _json_bytes_to_app_object(redis_client.get(key),return_class)


def set_by_key(some_object,key:str=None) -> None:
    if key is None:
        key = build_key(some_object.__class__)

    return redis_client.set(key, object_to_json(some_object))

def get_list_items_with_key(redis_list: str) -> List[Dict]:
    some_list = []

    for i in range(redis_client.llen(redis_list)):
        key = redis_client.lindex(redis_list, i)
        element_bytes = redis_client.get(key)
        new_element = _json_bytes_to_app_object(element_bytes,dict)

        some_list.append(new_element)

    return some_list

def get_list_items(redis_list: str) -> List[Dict]:
    some_list = []
    for i in range(redis_client.llen(redis_list)):
        element_bytes = redis_client.lindex(redis_list, i)
        new_element = _json_bytes_to_app_object(element_bytes,dict)
        some_list.append(new_element)
    return some_list
