# flake8: noqa: D100, D101

from byte import Collection, Model, Property, List
from byte_json import JsonModel

from arrow import Arrow
from decimal import Decimal
import arrow
import inspect


class Category(Model, JsonModel):
    class Options:
        collection = Collection()
        slots = True

    id = Property(int, primary_key=True)

    title = Property(str, max_length=50)
    description = Property(str, nullable=True)

    created_at = Property(Arrow, default=lambda: arrow.now())
    updated_at = Property(Arrow, default=lambda: arrow.now())


class Product(Model, JsonModel):
    class Options:
        collection = Collection()
        slots = True

    id = Property(int, primary_key=True)
    category = Property(Category)

    name = Property(str, max_length=50)
    description = Property(str, nullable=True)

    price = Property(Decimal)
    stock = Property(int)

    created_at = Property(Arrow, default=lambda: arrow.now())
    updated_at = Property(Arrow, default=lambda: arrow.now())


class CartItem(Model, JsonModel):
    class Options:
        collection = Collection()
        slots = True

    product = Property(Product)
    quantity = Property(int)

    created_at = Property(Arrow, default=lambda: arrow.now())
    updated_at = Property(Arrow, default=lambda: arrow.now())


class Cart(Model, JsonModel):
    class Options:
        collection = Collection()
        slots = True

    id = Property(int, primary_key=True)

    name = Property(str, max_length=50)
    items = Property(List(CartItem))

    created_at = Property(Arrow, default=lambda: arrow.now())
    updated_at = Property(Arrow, default=lambda: arrow.now())


class Customer(Model, JsonModel):
    class Options:
        collection = Collection()
        slots = True

    id = Property(int, primary_key=True)

    carts = Property(List(Cart))

    username = Property(str, max_length=100)
    password = Property(str, max_length=20)

    created_at = Property(Arrow, default=lambda: arrow.now())
    updated_at = Property(Arrow, default=lambda: arrow.now())


if __name__ == '__main__':
    def print_item(item):
        for key in dir(item):
            if key.startswith('_') or key[0].isupper():
                continue

            value = getattr(item, key)

            if inspect.isfunction(value) or inspect.ismethod(value):
                continue

            print(' - %-16s: %r' % (key, value))

        print('')

    # Category
    category_cables = Category.Objects.create(
        id=1,
        title='Cables'
    )

    category_cables.save()

    print_item(category_cables)

    # Product
    product_1 = Product.Objects.create(
        id=1,
        category=category_cables,
        name='USB to Micro USB (1m)',

        price=Decimal('3.59'),
        stock=35
    )

    print_item(product_1)

    product_2 = Product.Objects.create(
        id=2,
        category=category_cables,
        name='USB to Micro USB (5m)',

        price=Decimal('7.59'),
        stock=12
    )

    print_item(product_2)

    # Customer
    customer_1 = Customer.Objects.create(
        id=1,

        username='one',
        password='hunter12',

        carts=[
            Cart.Objects.create(
                id=1,
                name='2017-02-20',
                items=[
                    CartItem(product=product_1, quantity=3),
                    CartItem(product=product_2, quantity=5)
                ]
            )
        ]
    )

    print_item(customer_1)

    for cart in customer_1.carts:
        print_item(cart)

        for cart_item in cart.items:
            print_item(cart_item)

    #
    # Plain Encoder/Decoder
    #

    print('-' * 100)
    print('Plain Encoder/Decoder')
    print('-' * 100)

    # Category
    print(' '.join(['=' * 45, 'Category', '=' * 45]))

    encoded = category_cables.to_plain()

    print(encoded)
    print('')
    print_item(Category.from_plain(encoded))

    # Product
    print(' '.join(['=' * 45, 'Product', '=' * 45]))

    encoded = product_1.to_plain()

    print(encoded)
    print('')
    print_item(Product.from_plain(encoded))

    #
    # JSON Encoder/Decoder
    #

    print('-' * 100)
    print('JSON Encoder/Decoder')
    print('-' * 100)

    # Category
    print(' '.join(['=' * 45, 'Category', '=' * 45]))

    encoded = category_cables.to_json()

    print(encoded)
    print('')
    print_item(Category.from_json(encoded))

    # Product
    print(' '.join(['=' * 45, 'Product', '=' * 45]))

    encoded = product_1.to_json()

    print(encoded)
    print('')
    print_item(Product.from_json(encoded))
