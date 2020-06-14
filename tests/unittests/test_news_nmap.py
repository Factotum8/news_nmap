import unittest
from unittest import TestCase

from mock import Mock
from asynctest import TestCase, patch, CoroutineMock

from news_nmap.news_nmap import ServerMap
from news_nmap.news_nmap import RepositoriesFactory
from news_nmap.news_nmap import CacheRepositoryBuilder
from news_nmap.news_nmap import web


@patch('news_nmap.news_nmap.ServerMap._init_log_handler')
class TestServerMap(TestCase):

    @unittest.skip("")
    @patch('aiohttp.ClientSession.get')
    async def test_target_scraping(self, *args):
        size = 30
        server = ServerMap({'memory_depth': size})
        server.log = Mock()
        mock_get = args[0]
        with open('./tests/target_html_example.html') as f:
            mock_get.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[f.read()])
        result = await server.target_scraping('mock_val')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), size)

    # @patch('proxy_http.web.Response')
    # @patch('news_nmap.news_nmap.web')
    async def test__posts(self, *_):
        size = 5
        batch_stub = [
            {'id': '23519439', 'title': 'A',
             'url': 'https://callumprentice.github.io/apps', 'now': '2020-06-14T19:34:40.877048'},
            {'id': '23519816', 'title': 'B',
             'url': 'http://ed-thelen.org/comp-hist/B5000-AlgolRWaychoff.html', 'now': '2020-06-14T19:34:40.877048'},
            {'id': '23520240', 'title': 'D',
             'url': 'https://www.vidarholen.net/contents/blog/?p=878', 'now': '2020-06-14T19:34:40.877048'},
            {'id': '23519700', 'title': 'E',
             'url': 'https://sidsite.com/posts/autodiff/', 'now': '2020-06-14T19:34:40.877048'},
            {'id': '23515629', 'title': 'C',
             'url': 'https://github.com/pion/webrtc/tree/master/examples', 'now': '2020-06-14T19:34:40.877048'}
        ]
        server = ServerMap({'memory_depth': size})
        factory = RepositoriesFactory()
        factory.register_builder('cache', CacheRepositoryBuilder())
        server._cache_dao = await factory.create('cache')
        server.log = Mock()
        server.target_scraping = CoroutineMock(return_value=batch_stub)
        request = CoroutineMock()
        web = CoroutineMock()
        web.Response = CoroutineMock()
        request.query = {'offset': 0}

        _ = await server._posts(request)
        # TODO
        # web.Response.assert_called_with(text=str(batch_stub))
        # self.fail()

    def setUp(self):
        pass

    def tearDown(self):
        pass
