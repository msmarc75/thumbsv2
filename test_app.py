import unittest
from unittest.mock import patch, MagicMock
from app import app
from youtube_optimizer import YoutubeOptimizer

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Generateur de Miniatures YouTube', response.data.replace(b'\xc3\xa9', b'e'))

    @patch('app.YoutubeOptimizer')
    def test_generate_route(self, MockOptimizer):
        mock_instance = MockOptimizer.return_value
        mock_instance.process_videos.return_value = [
            {'title': 'Test Video', 'thumbnail': 'static/thumbnails/abc-123.jpg'}
        ]

        response = self.app.post('/generate', data={'titles': 'Test Video'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Video', response.data)
        # Verify call with use_uuids=True (default for manual input)
        mock_instance.process_videos.assert_called_with(['Test Video'], output_dir='static/thumbnails', use_uuids=True)

    @patch('app.fetch_channel_videos')
    def test_fetch_videos_route(self, mock_fetch):
        mock_fetch.return_value = [{'title': 'Vid 1', 'url': 'http://vid1'}]
        response = self.app.post('/fetch_videos', data={'channel_url': 'http://channel'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Vid 1', response.data)
        mock_fetch.assert_called_with('http://channel')

    @patch('app.YoutubeOptimizer')
    def test_generate_selection_route(self, MockOptimizer):
        mock_instance = MockOptimizer.return_value
        mock_instance.process_videos.return_value = []
        
        response = self.app.post('/generate_selection', data={'selected_titles': ['Vid 1', 'Vid 2']})
        self.assertEqual(response.status_code, 200)
        # Verify call with use_uuids=False
        mock_instance.process_videos.assert_called_with(['Vid 1', 'Vid 2'], output_dir='static/thumbnails', use_uuids=False)

    def test_optimizer_filename_sanitization(self):
        optimizer = YoutubeOptimizer(api_key="fake")
        # Test basic
        self.assertEqual(optimizer.sanitize_filename("Hello World"), "Hello World")
        # Test invalid chars
        self.assertEqual(optimizer.sanitize_filename("Foo/Bar:Baz?"), "FooBarBaz")
        # Test length
        long_title = "a" * 300
        sanitized = optimizer.sanitize_filename(long_title)
        self.assertEqual(len(sanitized), 200)

if __name__ == '__main__':
    unittest.main()
