# coding=utf-8
from __future__ import unicode_literals, absolute_import

import logging
from collections import defaultdict

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.forms import formset_factory
from django.http import HttpResponseBadRequest, JsonResponse, \
    HttpResponseNotAllowed
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, FormView, TemplateView

from .signals import order_created
from .models import ProductCategory, Product, DeliveryType, PaymentType, Order, ProductCustomFieldValue
from .forms import CartModifyForm, OrderForm, ProductOrderForm, \
    ReceiverForm, AddressForm, ProductFilterForm
from .cart import Cart, CartModificationError
from . import errors

logger = logging.getLogger(__name__)


class ProductCategoriesListView(ListView):
    """Список категорий в магазине"""

    model = ProductCategory

    def get_queryset(self):
        return self.model.objects.get_available()


class ProductCategoryFilterMixin(object):
    category_key = NotImplemented
    category = None
    get_only_available = True

    def get_queryset(self):
        self.category = get_object_or_404(
            ProductCategory, slug=self.kwargs.get(self.category_key))
        if self.get_only_available:
            qs = self.model.objects.get_available()
        else:
            qs = self.model.objects.all()
        qs = qs.filter(
            categories__pk=self.category.id).order_by('-in_stock', 'id')
        return qs.prefetch_related('categories', 'images')

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryFilterMixin,
                        self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProductListView(ProductCategoryFilterMixin, ListView):
    """Список товаров в категории"""

    model = Product
    category_key = 'slug'

    def _get_form(self):
        # fields = self.category.fields.filter(is_filter=True).prefetch_related('values')
        tvalues = ProductCustomFieldValue.objects.filter(
            Q(product__always_visible=True) | Q(product__is_unlimited=True) |
            Q(product__entries__quantity__gt=0), field__category=self.category).select_related('field').distinct()
        tfilters = defaultdict(list)
        for value in tvalues:
            tfilters[value.field].append(value)
        if not tfilters:
            return

        filters = [(x, tfilters[x]) for x in tfilters]
        return ProductFilterForm(self.category, filters, self.request.GET)

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        if self.form:
            context['form'] = self.form
        return context

    def get_queryset(self):
        qs = super(ProductListView, self).get_queryset()
        self.form = self._get_form()
        if self.form and self.form.is_valid():
            qs = self.form.filter_qs(qs)
        return qs


class ProductDetailView(ProductCategoryFilterMixin, DetailView):
    """Страница продукта"""

    model = Product
    category_key = 'cat_slug'
    get_only_available = False


class CartModifyFormView(FormView):
    """Ручка для изменения корзины в AJAX-запросе"""

    form_class = CartModifyForm

    def get(self, request, *args, **kwargs):
        # GET запросы не принимаем
        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return super(CartModifyFormView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        cart = Cart(self.request.session)
        success = True
        message = None
        try:
            form.perform_action(cart, self.request)
        except CartModificationError as e:
            success = False
            message = e.message

        basket_description = {
            'items_num': cart.items_num,
            'price': round(float(cart.price), 2),
        }
        if form.cleaned_data['response'] == self.form_class.RESPONSE_FULL:
            basket_description['items'] = []
            for product, amount, price in cart:
                basket_description['items'].append({
                    'product': {
                        'id': product.pk,
                        'name': product.name,
                        'url': product.get_absolute_url(),
                    },
                    'amount': amount,
                    'price': round(float(price), 2),
                })
        result = {'success': success, 'basket': basket_description}
        if message:
            result['message'] = message
        return JsonResponse(result)

    def form_invalid(self, form):
        return JsonResponse({'success': False})


class CheckoutFormView(TemplateView):
    """Страница подтверждения заказа"""

    template_name = 'django_shop/cart.html'

    def get(self, request, *args, **kwargs):
        cart = Cart(request.session)
        products_form = formset_factory(ProductOrderForm, extra=0)(
            initial=[{'product': p.id, 'amount': a} for p, a, _ in cart]
        )
        return super(CheckoutFormView, self).get(
            request, *args,
            order_form=OrderForm(),
            products_form=products_form,
            reciever_form=ReceiverForm(),
            address_form=AddressForm(),
            delivery_types=DeliveryType.objects.filter(is_active=True),
            payment_types=PaymentType.objects.filter(is_active=True),
            **kwargs
        )

    def post(self, request, *_, **kwargs):
        products_form = formset_factory(ProductOrderForm, extra=0)(
            request.POST)
        order_form = OrderForm(request.POST)
        receiver_form = ReceiverForm(request.POST)
        address_form = AddressForm(request.POST)
        try:
            with transaction.atomic():
                for f in (products_form, order_form, receiver_form,
                          address_form):
                    if not f.is_valid():
                        break
                else:
                    order = Order.from_forms(
                        products_form.cleaned_data, order_form.cleaned_data,
                        receiver_form.cleaned_data, address_form.cleaned_data,
                        request.session.session_key)
                    cart = Cart(request.session)
                    cart.clean()
                    order.send_emails()

                    order_created.send_robust(self, request=self.request, order=order)

                    if order.payment is not None and \
                            not order.payment.is_started:
                        return redirect(order.payment.get_payment_submit_url())
                    return redirect(order)

        except errors.DeliveryError:
            order_form.add_error(
                None, 'Ошибка при планировании доставки, убедитесь, '
                      'что вы верно ввели все данные'
            )

        except errors.PaymentError:
            order_form.add_error(
                None, 'Ошибка при обработке запроса на оплату'
            )
        except errors.ProductQuantityError:
            products_form.add_error(
                None, 'Ошибка при резервировании товара'
            )
        except Exception:
            logger.exception('Unexpected error on order creation')
            order_form.add_error(
                None, 'Неизвестная ошибка при создании заказа'
            )

        context = self.get_context_data(
            order_form=order_form,
            products_form=products_form,
            reciever_form=receiver_form,
            address_form=address_form,
            delivery_types=DeliveryType.objects.filter(is_active=True),
            payment_types=PaymentType.objects.filter(is_active=True),
            **kwargs
        )
        return self.render_to_response(context)


class OrderView(DetailView):
    """Страница с описанием товара. Доступна только тому, кто заказывал и стафу
    """

    model = Order
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        c = super(OrderView, self).get_context_data(**kwargs)
        if 'success' in self.request.GET:
            c['payment_success'] = int(self.request.GET['success'])
        else:
            c['payment_success'] = None
        return c

    def get_queryset(self):
        qs = super(OrderView, self).get_queryset()
        if settings.DEBUG or self.request.user.is_staff:
            return qs
        return qs.filter(sid=self.request.session.session_key)
