import datetime
import requests


class Vend:
    def __init__(self, company_name, access_token):
        self.company_name = company_name
        self.access_token = access_token
        self.base_url = "https://{}.vendhq.com/api".format(self.company_name)
        self.__params = {}
        self.data = []

    def __headers(self):
        # Set headers for request
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    def __build_build_url(self, endpoint, parameters=[]):
        # This is responsible to build request urls
        if parameters:
            p = '/'.join([str(param) for param in parameters]) + endpoint
            endpoint = "{}/{}".format(str(endpoint), p)

        return "{}/{}".format(self.base_url, endpoint)

    def __build_get_request(self, endpoint, parameters=None):
        # Build GET requests
        url = self.__build_build_url(endpoint, parameters=parameters)

        try:
            response = requests.get(url, headers=self.__headers(), params=self.__params)
            if response.status_code != 200:
                raise AssertionError()

            json_response = response.json()
            return json_response
        except Exception as e:
            # FIXME handle this
            return None

    def __get_response(self, endpoint, parameters=None):
        # manage response

        response = self.__build_get_request(endpoint=endpoint, parameters=parameters)

        return self.process_get_response(response=response, endpoint=endpoint)

    def process_get_response(self, response, endpoint):
        # Process responses
        if 'pagination' in response:
            self.pages = response['pagination']['pages']
            self.page = response['pagination']['page']
            self.data += response[endpoint]

            if self.page < self.pages:
                self.page += 1
                self.__params.update({'page': self.page})
                self.__get_response(endpoint)

        else:
            if endpoint in response:
                return response[endpoint]

            return response

        return self.data

    def get_customers(self, id=None, code=None, email=None, since=None):
        # Get list of customers
        parameters = self.__fix_parameters({
            "id": id,
            "code": code,
            "email": email,
            "since": since
        })

        return self.__get_response('customers', parameters=parameters)

    def get_customer(self, unique_id):
        # get single customer
        parameters = self.__fix_parameters({"unique_id": unique_id})

        return self.__get_response('customers', parameters=parameters)

    def add_customer(self, data={}):
        # Add customer POST
        return self.__get_response('customers', data=data)

    def get_products(self):
        # Get list of products, this will fetch all products and add it to an list object

        return self.__get_response(endpoint='products')

    def get_product(self, unique_id):
        # get single product
        return self.__get_response(endpoint='products', parameters=[unique_id])

    def add_product(self):
        # Add product POST

        return self.__build_get_request('products', parameters=[])

    def get_sales(self, since=None, tag=None, status=[], outlet_id=None):

        """
                This will get all sales since the beginning, this is resource intensive and not recommended.
                If you specify with parameter it will return all data in that time frame
                https://developers.vendhq.com/documentation/api/0.x/register-sales.html
                in the documentation: Dont rely on being able to get all the register sales for a retailer in a single API call.
        """

        parameters = self.__fix_parameters({'tag': tag, 'status': status,
                                            'outlet_id': outlet_id})

        response = self.__get_response(endpoint='register_sales', parameters=parameters)
        sales = []
        if since:
            for sale in response:
                sale_date = datetime.datetime.strptime(sale['sale_date'], "%Y-%m-%d %H:%M:%S")
                if sale_date >= datetime.datetime.strptime(since, "%Y-%m-%d"):
                    sales.append(sale)
            return sales

        return response

    def get_sale(self, unique_id):
        return self.__get_response(endpoint='register_sales', parameters=[unique_id])

    def add_sale(self, ):
        return self.__build_post_request('customers', data=data)

    def __fix_parameters(self, parameters):
        for parameter in parameters.keys():
            if not parameters[parameter]:
                parameters.pop(parameter)

        return parameters


"""
Stock Control
Customers
Outlets
Payment Types
Products
Register Sales
Registers
Suppliers
Taxes
Users
Webhooks
"""
