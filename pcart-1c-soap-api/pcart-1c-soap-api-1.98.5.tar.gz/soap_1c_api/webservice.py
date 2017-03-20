from soaplib.core.service import DefinitionBase, soap
from soaplib.core.model.primitive import String  # , Integer, Double
from soap_1c_api.models import XMLFile
from lxml import etree
from io import BytesIO
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from soap_1c_api.py2xml import Py2XML

import time
import hashlib
import zipfile
import base64


# def run_1c_task(path, job_meta={}):
#     job_id = job_meta['id']
#     t = mediator.publish(None, '1c_exchange:import', path, job_id)
#     result = get_message_result('1c_exchange:import', t)
#     return {'1c_exchange:import': result}


def write_to_file(xml):
    path = default_storage.save(
        '1c_exchange/%s.xml' % hashlib.sha1(
            str(time.ctime()).encode('utf-8')).hexdigest(),
        ContentFile(xml))
    return path


def get_as_xml(obj):
    items = ''
    for data in obj.get_data():
        attrs = u''
        for key in data:
            attrs += u' {key}="{value}"'.format(key=key, value=data[key])
        items += u'<{item_name}{attrs} />\n'.format(
            item_name=obj.item_name, attrs=attrs
        )
    return u'<{name}>\n{items}</{name}>'.format(name=obj.name, items=items)


class ExchangeWebService(DefinitionBase):
    '''SOAP Import/Export interface for 1C
    '''
    def __init__(self, environ):
        '''
        This saves a reference to the request environment
        on the current instance
        '''
        self.environ = environ
        super(ExchangeWebService, self).__init__(environ)

    @soap(String, _returns=String)
    def import_goods(self, xml_body):
        xml_body = base64.b64decode(xml_body)
        try:
            zip_xml = zipfile.ZipFile(BytesIO(xml_body))
            xml_body = zip_xml.open(zip_xml.namelist()[0]).read()
        except zipfile.BadZipfile:
            pass  # TODO: add logger info
        '''Require the next xml:
        <timeout>10</timeout>
        '''
        # scs = 10
        scs = len(xml_body) / 1000
        path = write_to_file(xml_body)
        # create xmlfile in DB
        t = XMLFile.objects.create(filename=path)
        r = t.run_import_task()
        return base64.b64encode('''<result>
<task_id>%s</task_id>
<waiting_time>%d</waiting_time>
<success>True</success>
</result>'''.encode('utf-8') % (r.id, scs + 30))

    @soap(_returns=String)
    def export_orders(self):
        from pcart_cart import Order
        from collections import OrderedDict
        from xml.sax.saxutils import escape
        import pytz

        ESCAPE_CHARS = {
            '"': "&quot;",
            "'": "&apos;",
            "&": "&amp;",
            ">": "&gt;",
            "<": "&lt;",
        }

        def text_escape(text):
            return escape(text, ESCAPE_CHARS)

        message = ''

        orders = []
        queryset = Order.objects.filter(export_status='notset')
        for order in queryset:
            products_items = []
            services = []
            for i in order.items():
                if i['item_type'] in ['product', 'variant']:
                    products_items.append(OrderedDict([
                        ('product_name', text_escape(i['object'].title)),
                        ('product_price', i['price']),
                        ('product_amount', i['quantity']),
                        ('price', i['line_price']),
                        ('product__uid', i['item_id']),
                        ('product__price', i['object'].price),
                    ]))
                else:
                    services.append(OrderedDict([
                        ('product_name', text_escape(i['object'].title)),
                        ('product_price', i['price']),
                    ]))

            orders.append(OrderedDict([
                ('id', order.id),
                ('datetime', '{:%Y-%m-%d%H%M%S}'.format(
                    order.added.astimezone(
                        pytz.timezone(settings.TIME_ZONE)
                    )
                )),
                ('number', text_escape(order.number)),
                ('price', order.total_price),
                ('currency', settings.PCART_DEFAULT_CURRENCY),
                ('customer', {
                    'id': order.customer.id,
                    'full_name': order.customer.name,
                    'phones': [{
                        'number': order.customer.user.phone,
                        'type': '-----',
                        }],
                    'addresses': [{
                        'value': text_escape(order.get_shipping_info()),
                        }],
                    'email': {
                        'value': order.customer.user.email,
                    },
                }),
                ('shippingmethod', {
                    'type': text_escape(order.get_shipping_method_name()),
                }),
                ('paymentmethod', {
                    'type': text_escape(order.get_payment_method_name()),
                }),
                ('products', products_items),
                ('services', services),
                ('comment', order.note),
            ]))

        message += Py2XML().parse(
            {'orders': orders}).replace('><', '>\n<')
        if not message:
            message = '''<result>
<task_id>0</task_id>
<waiting_time>0</waiting_time>
<success>True</success>
</result>'''
        message = '<v8msg>%s</v8msg>' % message
        return base64.b64encode(message.encode('utf-8'))

    @soap(String, _returns=String)
    def set_export_status(self, xml_body):
        from pcart_cart.models import Order, OrderStatus
        xml_body = base64.b64decode(xml_body)
        zip_xml = zipfile.ZipFile(BytesIO(xml_body))
        xml_body = zip_xml.open(zip_xml.namelist()[0]).read()
        root = etree.XML(xml_body)
        received = root.xpath('orders/received/order')
        statuses = root.xpath('orders/statuses')

        if received:
            received_numbers = [a.get('number') for a in received]
            queryset = Order.objects.filter(number__in=received_numbers)
            queryset.update(export_status='success')

        if statuses:
            data = statuses[0].getchildren()
            for chunk in data:
                if 'status' in chunk and 'number' in chunk:
                    try:
                        status = OrderStatus.objects.get(
                            slug=chunk['status'])
                    except OrderStatus.DoesNotExist:
                        status = OrderStatus(
                            name=chunk['status'].capitalize(),
                            slug=chunk['status'],
                        )
                        status.save()
                    Order.objects.filter(number=chunk['number'])\
                        .update(status=status)

        return base64.b64encode('''<result>
<success>True</success>
</result>'''.encode('utf-8'))

    @soap(String, _returns=String)
    def check_status(self, task_id):
        from .tasks import import_goods
        task = import_goods.AsyncResult(task_id)
        status = task.status

        if status == 'PROGRESS':
            status = 'pending'
        elif status == 'SUCCESS':
            status = 'success'
        elif status == 'FAILURE':
            status = 'failed'
        return base64.b64encode(('''<result>
<status>%s</status>
</result>''' % (status,)).encode('utf-8'))

    @soap(String, _returns=String)
    def get_import_result(self, task_id):
        from .tasks import import_goods
        task = import_goods.AsyncResult(task_id)
        result = task.result
        output = ''
        if result:
            for key, value in result.items():
                output += '<error uuid="%s" message="%s" />\n' % (key, value)
        return base64.b64encode(('''<v8msg>
<errors>%s</errors>
</v8msg>''' % (output,)).encode('utf-8'))

    @soap(_returns=String)
    def pending_tasks(self):
        # pending_tasks = task_manager.get_pending_tasks()
        pending_tasks = []
        output = '\n'.join(
            ['<task_id>%d</task_id>' % x for x in pending_tasks]
        )
        return base64.b64encode(('''<result>
%s
</result>''' % (output,)).encode('utf-8'))
