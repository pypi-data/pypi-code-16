"""Unit tests for webservicex-converttemp. """
from unittest import TestCase
from unittest.mock import patch
from . import ConvertTemperature


class ConvertTemperatureTestCase(TestCase):
    """Testing the ConvertTemperature client. """

    def setUp(self):
        zeep_patcher = patch('zeep.Client')
        self.mock_zeep = zeep_patcher.start()
        self.mock_client = self.mock_zeep.return_value
        self.mock_service = self.mock_client.service
        self.client = ConvertTemperature()
        self.addCleanup(zeep_patcher.stop)

    def test_tempearture_scale_lookup(self):
        """Check it is possible to convert between standardised temperature
        scale names and the names defined by the webservice.
        """
        convert_scale_name = ConvertTemperature.convert_scale_name
        self.assertEqual(convert_scale_name('CELSIUS'), 'degreeCelsius')
        self.assertEqual(convert_scale_name('FAHRENHEIT'), 'degreeFahrenheit')
        self.assertEqual(convert_scale_name('RANKINE'), 'degreeRankine')
        self.assertEqual(convert_scale_name('REAUMUR'), 'degreeReaumur')
        self.assertEqual(convert_scale_name('KELVIN'), 'kelvin')

    def test_client(self):
        """Check a ConvertTemperature client is constructed with a zeep client
        configured to the correct endpoint.
        """
        self.assertEqual(self.client.service, self.mock_service)

    def test_convert_temp_call(self):
        """Check that a temperature conversion makes the correct call to the
        underlying webservice.
        """

        self.client.convert_temp(
            input_value=-40,
            input_scale='CELSIUS',
            output_scale='FAHRENHEIT')

        self.mock_service.ConvertTemp.assert_called_once_with(
            -40, 'degreeCelsius', 'degreeFahrenheit')

    def test_convert_temp_value(self):
        """Check that a temperature conversion returns the correct value from
        the webservice.
        """

        self.mock_service.ConvertTemp.return_value = -40

        output_value = self.client.convert_temp(
            input_value=-40,
            input_scale='CELSIUS',
            output_scale='FAHRENHEIT')

        self.assertEqual(type(output_value), float)
        self.assertEqual(output_value, -40.0)
