from decimal import Decimal

from .models import Product, PackagingBox


class CartModificationError(Exception):
    def __init__(self, message):
        self.message = message


class Cart(object):
    """Объект корзины клиента. Данные о покупках хранятся в сессии на
    стороне сервера
    """

    CART = '__cart'

    def __init__(self, session):
        """
        :type session: django.contrib.sessions.backends.base.SessionBase
        """
        self._session = session
        if self.CART in self._session:
            self._products = self.load(self._session[self.CART])
        else:
            self._products = []

    def save(self):
        """Сохранить корзину в сессию"""
        data = [(p['product'].id, float(p['amount'])) for p in self._products]
        self._session[self.CART] = data

    @staticmethod
    def load(basket_data):
        """Загрузить из списка с данными о состоянии корзины структуру,
        описывающую корзину в классе

        :type basket_data: list[(int, float)]

        :rtype: list[dict[django_shop.models.Product, decimal.Decimal]]
        """
        result = []
        for product_id, amount in basket_data:
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                continue
            else:
                result.append({'product': product, 'amount': Decimal(amount)})
        return result

    @staticmethod
    def _check_amount(product_obj, amount):
        if not product_obj.is_weight and not float(amount).is_integer():
            raise CartModificationError(
                '{} нельзя купить частично'.format(product_obj)
            )
        if product_obj.is_unlimited:
            return
        if product_obj.in_stock < amount:
            raise CartModificationError(
                'К сожалению, на складе недостаточно товара {} для '
                'добавления в корзину'.format(product_obj)
            )

    def _create(self, product_obj, amount):
        product = {
            'product': product_obj,
            'amount': amount
        }
        self._products.append(product)

    def add(self, product_obj, amount):
        """Добавить указанное количество продукта в корзину

        :type product_obj: django_shop.models.Product
        :type amount: decimal.Decimal
        """
        for product in self._products:
            if product['product'] == product_obj:
                new_amount = product['amount'] + amount
                self._check_amount(product_obj, new_amount)
                product['amount'] = new_amount
                break
        else:
            self._check_amount(product_obj, amount)
            self._create(product_obj, amount)

        self.save()

    def remove(self, product_obj):
        """Удалить продукт из корзины

        :type product_obj: django_shop.models.Product
        """
        remove = None
        for num, product in enumerate(self._products):
            if product['product'] == product_obj:
                remove = num
                break

        if remove is not None:
            self._products.pop(remove)
            self.save()

    def set(self, product_obj, amount):
        """Установить количество продукта в корзине

        :type product_obj: django_shop.models.Product
        :type amount: decimal.Decimal
        """
        for product in self._products:
            if product['product'] == product_obj:
                self._check_amount(product_obj, amount)
                product['amount'] = amount
                break
        else:
            self._check_amount(product_obj, amount)
            self._create(product_obj, amount)

        self.save()

    def get_amount(self, product_obj):
        """Узнать количество продукта в корзине

        :type product_obj: django_shop.models.Product
        """
        for product in self._products:
            if product['product'] == product_obj:
                return product['amount']
        return 0

    def clean(self):
        """Очистить корзину"""
        self._products = []
        self.save()

    @property
    def price(self):
        """Цена всех продуктов в корзине"""
        return sum(p['product'].price * p['amount'] for p in self._products)

    @property
    def weight(self):
        """Вес всех продуктов в корзине"""
        return sum(p['product'].weight * p['amount'] for p in self._products)

    @property
    def measures(self):
        """Измерения прямоуголной коробки, в которую поместятся все продукты в
        корзине
        """
        return PackagingBox.get_measures_for_products(
            p['product'] for p in self._products)

    @property
    def items_num(self):
        """Количество продуктов в корзине"""
        return len(self._products)

    @property
    def is_empty(self):
        return self.items_num == 0

    def __iter__(self):
        return (
            (p['product'], p['amount'],
             p['product'].price * Decimal(p['amount'])) for p in self._products
        )

    def __bool__(self):
        return bool(self._products)
