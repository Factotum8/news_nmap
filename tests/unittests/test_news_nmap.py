from mock import Mock
from asynctest import TestCase, patch, CoroutineMock

from news_nmap.news_nmap import ServerMap


@patch('news_nmap.news_nmap.ServerMap._init_log_handler')
class TestServerMap(TestCase):

    # @unittest.skip("")
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

    def setUp(self):
        pass

    def tearDown(self):
        pass
