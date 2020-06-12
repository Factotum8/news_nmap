"""
Factory method pattern for async repositories
"""
from abc import ABC, abstractmethod

__all__ = ['ObjectFactory', 'ObjectRepository', 'ObjectBuilder']


class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    async def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return await builder(**kwargs)


class ObjectRepository(ABC):

    def __init__(self, connection):
        self._connection = connection

    @abstractmethod
    def close(self):
        pass


class ObjectBuilder(ABC):

    def __init__(self):
        self._instance = None

    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def connect(self):
        pass
