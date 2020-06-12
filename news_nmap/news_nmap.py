import os
import sys
import yaml
import logging
import asyncio
import argparse
from typing import Dict
from pathlib import Path
from typing import Union
from collections import ChainMap

import aiohttp
from aiohttp import web
import logstash
import cacheout

sys.path.insert(0, './mypackages')
from mypackages import settings
from mypackages import object_factory


class ServerMap:
    """
    Main class
    """
    def __init__(self, config: Dict[str, Union[str, int]]):

        self.log = None
        self._factory = None
        self._redis_dao = None
        # Remove prefix nmap_ for environment variables
        self._config = {remove_prefix(k, 'nmap_'): v for k, v in config.items()}

        self._cache_maxsize = self._config['memory_depth']
        # self._cache = cacheout.fifo.FIFOCache(self._cache_maxsize)

        self._init_log_handler()

        self._app = web.Application()
        self._app.on_startup.append(self._initialize)
        self._app.on_shutdown.append(self._terminate)
        # handler init
        self._app.router.add_get('/posts', self._posts)

    async def _initialize(self, app):
        self.log.info('Server is starting')

        self._factory = RepositoriesFactory()
        # Register cache repository
        self._factory.register_builder('cacheout', CacheRepositoryBuilder())
        self._cache_dao = await self._factory.create('cacheout')  # cache data access object
        self._cache_dao.batch.update('1', 1)
        self._cache_dao.batch.update('2', 2)
        self._cache_dao.batch.update('3', 3)
        print(self._cache_dao.batch[1:])
        pass

    async def _terminate(self, app):
        self.log.info('Server is shutting down')
        # The insurance in case if method 'self._redis_dao.close' didn't call explicitly
        try:
            await self._redis_dao.close()
        except Exception:
            pass

    async def _posts(self, request):
        print("hello")

    def _init_log_handler(self):
        """
        First handler always write to console.
        Second handler may write to file or elastic stack
        :return:
        """
        try:
            handlers = []
            if self._config['log_handler'] == 'file':
                # create the logging file handler
                try:
                    Path(self._config['path_to_log']).mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    pass

                self.log = logging.getLogger(f"{__name__}-python-file-logger")

                log_handler_ = logging.FileHandler(
                    filename=self._config['path_to_log'], encoding=None, delay=False
                )
                format_str = u'%(asctime)s#%(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s'
                format_obj = logging.Formatter(format_str)
                log_handler_.setFormatter(format_obj)
                handlers.append(log_handler_)

            elif self._config['log_handler'] in ('stash', 'logstash'):
                # create the logging logstash handler
                self.log = logging.getLogger(f'{__name__}-python-logstash-logger')
                log_handler = logstash.TCPLogstashHandler(host=self._config['logging_logstash_host'],
                                                          port=self._config['logging_logstash_port'],
                                                          version=1)
                handlers.append(log_handler)

            # always write to console
            self.log = self.log if handlers else logging.getLogger(f'{__name__}-python-stdout-logger')
            log_handler = logging.StreamHandler(sys.stdout)
            format_str = u'%(asctime)s#%(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s'
            format_obj = logging.Formatter(format_str)
            log_handler.setFormatter(format_obj)
            handlers.append(log_handler)

            # example self.log.setLevel(logging.WARNING)
            self.log.setLevel(self._config['logging_level'].upper())

            list(map(self.log.addHandler, handlers))  # Added all handlers to logger

        except KeyError as e:
            raise KeyError(f"Specify necessary environment variable {e}")

    def listen(self):
        web.run_app(self._app, host=self._config['host'], port=self._config['port'])


class RepositoriesFactory(object_factory.ObjectFactory):
    """
    The RepositoriesFactory is an alias to ObjectFactory
    It is the creator from pattern factory method
    """


# self._cache = cacheout.fifo.FIFOCache(self._cache_maxsize)
class CustomCache(cacheout.fifo.FIFOCache):

    def __getitem__(self, item):
        """

        :param item: slice(1, None, None)
        :return:
        """
        # TODO
        return super().__getitem__(item)

    async def update(self, key, value):
        await self.save(key, value)

    async def save(self, key, value):
        self._cache.set(key, value)


class CacheRepository(object_factory.ObjectRepository):
    """
    TODO product
    """
    def __init__(self, connection: CustomCache):
        self._cache = connection  # Redefining the interface for the application context
        super().__init__(connection)

    def close(self):
        self._connection.clear()
        del self

    @property
    def batch(self):
        return self._cache


class CacheRepositoryBuilder(object_factory.ObjectBuilder):
    """
    TODO client
    """
    async def __call__(self, cache_maxsize: int = 30, **_ignored):
        if not self._instance:
            cache_obj = await self.create_repository(cache_maxsize)
            self._instance = CacheRepository(cache_obj)
        return self._instance
        pass

    async def create_repository(self, cache_maxsize: int = 30, **_ignored):
        return await self.connect(cache_maxsize)

    async def connect(self, cache_maxsize: int = 30):
        try:
            return CustomCache(cache_maxsize)
        except Exception as e:
            print(f"Can't create cacheout: {e}")
            raise


def remove_prefix(text, prefix):
    # on Python 3.9+ you can use text.removeprefix(prefix)
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def main(path_to_config: str):

    server = ServerMap(settings.load_config(path_to_config))
    server.listen()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", action='store', type=str, dest='PATHTOCONFIG',
                            help="Specify the path to the config  file")
    args = arg_parser.parse_args()
    main(args.PATHTOCONFIG)
