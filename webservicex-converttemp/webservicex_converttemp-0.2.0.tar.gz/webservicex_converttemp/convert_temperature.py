"""A client to interface with a temperature conversion webservice. """
import zeep

WSDL = "http://www.webservicex.net/ConvertTemperature.asmx?wsdl"

TEMPERATURE_SCALE_NAME_MAPPING = {
    'KELVIN': 'kelvin',
    'CELSIUS': 'degreeCelsius',
    'FAHRENHEIT': 'degreeFahrenheit',
    'REAUMUR': 'degreeReaumur',
    'RANKINE': 'degreeRankine',
}


class ConvertTemperature():
    """This client corresponds to the WebserviceX.NET ConvertTemperature
    webservice endpoint. It exposes the convert_temp method which calls
    ConvertTemp on the webserivce..
    """

    @staticmethod
    def convert_scale_name(scale_name):
        """Convert between standardised temperature scale names and those
        defined by the webservice.
        """
        return TEMPERATURE_SCALE_NAME_MAPPING[scale_name]

    def __init__(self):
        client = zeep.Client(WSDL)
        self.service = client.service

    def convert_temp(self, *, input_value=None, input_scale=None,
                     output_scale=None):
        """Convert a temperature value from one scale to another
        Args:
            input_value (float): starting temperature value
            input_scale (string): starting temperature scale
            output_scale (string): target temperature scale
        """
        converted_input_scale = self.convert_scale_name(input_scale)
        converted_output_scale = self.convert_scale_name(output_scale)
        returned_output_value = self.service.ConvertTemp(
            input_value, converted_input_scale, converted_output_scale)

        output_scale = float(returned_output_value)

        return output_scale
