import unittest
from unittest.mock import patch, Mock
import main
import fixtures


class TestYourCode(unittest.TestCase):
    @patch('main.requests.get')
    @patch('main.INFLUXDBCLIENT')
    def test_process_and_insert_data(self, mock_influxdb, mock_requests_get):
        # Create a mock InfluxDB client
        mock_influxdb.return_value = Mock()

        # Create a mock response for the API call
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = fixtures.data

        # Set the return value of the mocked API call
        mock_requests_get.return_value = mock_response

        # Call the function in your module that interacts with the API and InfluxDB
        main.main()

        # Assert that the API call was made with the expected URL
        mock_requests_get.assert_called_once_with(main.URL,
                                                  headers={'Content-Type': 'application/json', 'X-Api-Key': None})


if __name__ == '__main__':
    unittest.main()
