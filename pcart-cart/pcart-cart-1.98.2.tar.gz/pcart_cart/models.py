from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
import uuid
from decimal import Decimal
from pcart_customers.models import Customer


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(
        Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='carts')
    customer = models.ForeignKey(
        Customer, verbose_name=_('Customer'), on_delete=models.CASCADE, related_name='carts')

    content = JSONField(_('Content'), default=list, blank=True)
    note = models.TextField(_('Note'), default='', blank=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        unique_together = ['site', 'customer']

    def __str__(self):
        return str(self.customer)

    def items(self):
        from pcart_catalog.models import Product, ProductVariant
        result = self.content
        i = 0
        for item in result:
            item['id'] = i
            i += 1
            if item['item_type'] == 'product':
                item['product'] = Product.objects.get(id=item['item_id'])
                item['object'] = item['product']
            elif item['item_type'] == 'variant':
                item['variant'] = ProductVariant.objects.select_related('product')\
                    .prefetch_related('product__images').get(id=item['item_id'])
                item['product'] = item['variant'].product
                item['object'] = item['variant']
        return result

    def item_count(self):
        return len([x for x in self.content if x['item_type'] in ['product', 'variant']])

    def total_weight(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['weight'])
        return float(result)

    def total_price(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['price'])
        return float(result)

    def change_item_quantity(self, id, quantity, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            _qty = int(quantity)
            if _qty == 0:
                self.remove_item(id, save=False)
            else:
                self.content[id]['quantity'] = _qty
                self.content[id]['line_price'] = float(_qty * Decimal(self.content[id]['price']))
            if save:
                self.save()

    def remove_item(self, id, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            del self.content[id]
            if save:
                self.save()

    def add_item(self, item_id, item_type='product', quantity=1, price=0.00, weight=0, commit=True):
        item = {
            'item_id': item_id,
            'item_type': item_type,
            'quantity': int(quantity),
            'price': float(price),
            'weight': float(weight),
            'line_price': float(Decimal(quantity)*Decimal(price)),
        }
        _append = True
        for i in self.content:
            if i['item_id'] == item_id and i['item_type'] == item_type:
                _append = False
                _qty = Decimal(i['quantity']) + Decimal(quantity)
                i['quantity'] = int(_qty)
                i['price'] = float(price)
                i['line_price'] = float(_qty*Decimal(price))
        if _append:
            self.content.append(item)
        if commit:
            self.save()

    def clear(self, save=True):
        self.content = list()
        self.note = ''
        if save:
            self.save()

    def copy_from(self, another_cart, save=True):
        self.content = another_cart.content
        self.note = another_cart.note
        if save:
            self.save()


class OrderNumberFormat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.OneToOneField(
        Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='order_number_format')

    template = models.CharField(_('Template'), default='P%06d', max_length=20)
    last_number = models.PositiveIntegerField(_('last number'), default=0)

    class Meta:
        verbose_name = _('Order number format')
        verbose_name_plural = _('Order number formats')

    def __str__(self):
        return self.template % self.last_number

    def increase_number(self, delta=1, save=True):
        self.last_number += delta
        if save:
            self.save()
        return self.last_number


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(_('Number'), max_length=50, unique=True)

    site = models.ForeignKey(
        Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='orders')
    customer = models.ForeignKey(
        Customer, verbose_name=_('Customer'), on_delete=models.CASCADE, related_name='orders')

    content = JSONField(_('Content'), default=list, blank=True)

    shipping_data = JSONField(_('Shipping data'), default=dict, blank=True)
    payment_data = JSONField(_('Payment data'), default=dict, blank=True)

    note = models.TextField(_('Note'), default='', blank=True)

    total_price = models.DecimalField(_('Total price'), max_digits=10, decimal_places=2, default=0.00)
    total_weight = models.FloatField(_('Total weight (kg)'), default=0.0)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return self.number

    def _get_total_weight(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['weight'])
        return float(result)

    def _get_total_price(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['price'])
        return float(result)

    def save(self, *args, **kwargs):
        self.total_price = self._get_total_price()
        self.total_weight = self._get_total_weight()
        super(Order, self).save(*args, **kwargs)

    def item_count(self):
        return len([x for x in self.content if x['item_type'] in ['product', 'variant']])

    def items(self):
        from pcart_catalog.models import Product, ProductVariant
        result = self.content
        i = 0
        for item in result:
            item['id'] = i
            i += 1
            if item['item_type'] == 'product':
                item['product'] = Product.objects.get(id=item['item_id'])
                item['object'] = item['product']
            elif item['item_type'] == 'variant':
                item['variant'] = ProductVariant.objects.select_related('product')\
                    .prefetch_related('product__images').get(id=item['item_id'])
                item['product'] = item['variant'].product
                item['object'] = item['variant']
        return result

    def send_message(self):
        """Send messages to the customer and moderation team."""
        from pcart_messaging.utils import create_email_message
        from pcart_customers.models import User
        from django.conf import settings
        sender = settings.DEFAULT_FROM_EMAIL
        context = {
            'order': self,
        }
        if self.customer.user:
            recipients = [self.customer.user.email]
            msg = create_email_message('order', recipients, sender, context)
            msg.send()

        # Looking for a group "order" for sending the info about new order
        users = User.objects.filter(groups__name='order')
        if users:
            recipients = list(users.values_list('email', flat=True))
            msg = create_email_message('order_moderation', recipients, sender, context)
            msg.send()

    def change_item_quantity(self, id, quantity, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            _qty = int(quantity)
            if _qty == 0:
                self.remove_item(id, save=False)
            else:
                self.content[id]['quantity'] = _qty
                self.content[id]['line_price'] = float(_qty * Decimal(self.content[id]['price']))
            if save:
                self.save()

    def remove_item(self, id, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            del self.content[id]
            if save:
                self.save()

