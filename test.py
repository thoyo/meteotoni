import unittest
from unittest.mock import patch, Mock
import main
import fixtures
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")


class TestYourCode(unittest.TestCase):
    @patch('main.INFLUXDBCLIENT')
    @patch('main.requests.get')
    def test_process_and_insert_data(self, mock_requests_get, mock_influxdb):
        mock_influxdb.return_value = Mock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = fixtures.data
        mock_requests_get.return_value = mock_response

        main.main()

        mock_requests_get.assert_called_once_with(main.URL,
                                                  headers={'Content-Type': 'application/json',
                                                           'X-Api-Key': api_key})


if __name__ == '__main__':
    unittest.main()
