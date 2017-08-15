import importlib
import os
import pkgutil

__all_intents = {}


def register(intent):
    __all_intents[intent.name()] = intent


def all():
    return __all_intents


class Base:
    def name(self):
        return self.__class__.__name__

    def definition(self):
        raise NotImplementedError()

    def fulfill(self, slots):
        raise NotImplementedError()

pkg_dir = os.path.dirname(__file__)
for _, name, _ in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)
