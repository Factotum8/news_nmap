import sys
import logging
import datetime
import argparse
from typing import Dict
from pathlib import Path
from typing import Union

import logstash
import asyncio
import aiohttp
from aiohttp import web
from bs4 import BeautifulSoup

from mypackages import settings
from mypackages import object_factory


class ServerMap:
    """
    Main class
    """
    log = None

    allowed_keys = ['id', 'title', 'url', 'now']  #  allowed key list to sort

    def __init__(self, config: Dict[str, Union[str, int]]):

        self.log = None
        self._factory = None
        # Remove prefix nmap_ for environment variables
        self._config = {remove_prefix(k, 'nmap_'): v for k, v in config.items()}

        self._cache_maxsize = self._config['memory_depth']

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
        self._factory.register_builder('cache', CacheRepositoryBuilder())
        self._cache_dao = await self._factory.create('cache')  # cache data access object

        if (batch := await self.target_scraping()) is None:
            s = f"can't complete the news batch"
            self.log.warning(s)
            raise KeyboardInterrupt(s)
        # save news
        self._cache_dao.batch.extend(batch)

    async def _terminate(self, app):
        self.log.info('Server is shutting down')
        # The insurance in case if method 'self._redis_dao.close' didn't call explicitly
        try:
            await self._cache_dao.close()
        except Exception:
            pass

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

    async def _posts(self, request):
        try:
            order = request.query.get('order') or 'id'
            offset = int(request.query.get('offset')) or 0
            limit = int(request.query.get('limit')) or 5

            # Updating the cache on request
            self._cache_dao.batch.extend(await self.target_scraping())

            if order not in self.allowed_keys:
                raise ValueError(f"not allowed sort key: {order}")

            if offset < 0 or offset > self._cache_maxsize:
                return web.Response(text=str('Offset is too large or negative'))

            if limit < 0 or limit > self._cache_maxsize:
                return web.Response(text=str('Offset is too large or negative'))

            if (subset := sorted(self._cache_dao.batch, key=lambda x: x[order])[offset: offset + limit]) is None:
                return web.HTTPInternalServerError()

            return web.Response(text=str(subset))

        except ValueError as e:
            self.log.debug(f"{request} isn't correct parameters: {e}")
            return web.HTTPBadRequest()
        except Exception as e:
            self.log.exception(f"{request} throw exception: {e}")
            raise

    async def target_scraping(self, target=None):
        """
        The method parses target resource
        :return: batch - list with dicts or None
        """
        target = target or self._config['target_fqdn']
        self.log.debug(f"{target} is starting parse")
        batch = []
        try:
            async with aiohttp.ClientSession() as session, session.get(target) as response:
                soup = BeautifulSoup(await response.text())
                # Date time in UTC format
                now_ = datetime.datetime.utcnow().isoformat()
                # TODO It may be optimized: soup.find_next('tr', {'class': 'athing'})
                for _, item in zip(range(self._cache_maxsize), soup.find_all('tr', {'class': 'athing'})):
                    story = item.find('a', {'class': 'storylink'})
                    batch.append({
                        'id': item['id'],
                        'title': story.text,
                        'url': story['href'],
                        'now': now_
                    })
        except asyncio.CancelledError:
            raise
        except aiohttp.ClientError as e:
            self.log.error(f"Can't connect to target resource, error: {e}")
        except Exception as e:
            self.log.exception(f"Can't parse target source, error: {e}")
        finally:
            return batch or None

    def listen(self):
        web.run_app(self._app, host=self._config['host'], port=self._config['port'])


class RepositoriesFactory(object_factory.ObjectFactory):
    """
    The RepositoriesFactory is an alias to ObjectFactory
    It is the creator from pattern factory method
    """


class CustomCache(list):
    """
    This implementation for example!
    In real project could replace to Redis or something else
    """

    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        super().__init__()

    def __getitem__(self, item):
        """

        :param item: slice(start, end, step)
        :return:
        """
        try:
            start, end, _ = item

            if start < 0 or start > self.maxsize:
                raise ValueError('start is too large or negative')

            if end < 0 or end > self.maxsize:
                raise ValueError('end is too large or negative')

            return super().__getitem__(item)
        except Exception:
            return None

    def extend(self, __iterable) -> None:
        if __iterable is not None:
            self.clear()
            super(CustomCache, self).extend(__iterable)


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
            print(f"Can't create cache repo: {e}")
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
