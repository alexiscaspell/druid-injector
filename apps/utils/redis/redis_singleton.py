import redis
from apps.configs.vars import Vars
import apps.configs.configuration as cf


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisLocalPool(metaclass=Singleton):

    def __init__(self, host=cf.get(Vars.REDIS_HOST), port=int(cf.get(Vars.REDIS_PORT)), db=0,password=cf.get(Vars.REDIS_PASSWD)):
        self.redisPool = redis.ConnectionPool(host=host, port=port, db=db,password=password)

    def __getattr__(self, name):
        return self.redisPool.__getattribute__(name)

redis_local_pool = RedisLocalPool().redisPool
