from copy import deepcopy
from enum import Enum


def model_metadata(args):
    def decorate(func):
        func.__model_metadata__ = args
        return func
    return decorate


class AppModel(object):

    __model_metadata__ = {}

    def __new__(cls, *args,**kwargs):
        for attr in args:
            if hasattr(attr, '__model_metadata__'):
                AppModel.__model_metadata__ = attr.__model_metadata__
        return super().__new__(cls)

    def to_dict(self):

        self_dict = deepcopy(self.__dict__)

        for key, value in self.__dict__.items():

            if hasattr(value.__class__, 'to_dict'):
                self_dict[key] = value.to_dict()

        for attrname in dir(self.__class__):
            if isinstance(getattr(self.__class__, attrname), property):
                self_dict[attrname] = getattr(self, attrname)

        return self_dict

    @classmethod
    def _format_parameter(cls, some_object, some_class):
        if issubclass(some_class, AppModel):
            return some_class.from_dict(some_object)
        elif issubclass(some_class, Enum):
            return some_class(some_object)

    @classmethod
    def from_dict(cls, some_dict):

        new_dict = deepcopy(some_dict)

        for arg in cls.__model_metadata__:
            if arg in some_dict:
                new_dict.update({arg: cls._format_parameter(
                    some_dict[arg], cls.__model_metadata__[arg])})

        try:
            return cls(**new_dict)
        except Exception as _:
            return cls(new_dict)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.to_dict())
