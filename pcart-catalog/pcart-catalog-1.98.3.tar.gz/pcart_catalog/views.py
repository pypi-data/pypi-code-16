# from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import Http404, QueryDict, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import (
    Q, Prefetch, Count, Sum, Case,
    Min, Max, When,
    PositiveIntegerField, DecimalField, F)
from django.core.cache import cache
from django.conf import settings
from . import settings as pcart_settings
from .models import (
    Collection,
    Product,
    ProductVariant,
    ProductStatus,
    ProductType,
    ProductTypeProperty,
)
from .utils import (
    split_collection_slug,
    filter_slug_to_tags,
    group_tags_for_prefixes,
    regroup_tags_for_filter_sets,
    get_tags_array_query_expression,
    normalize_filter_tags,
)


AVAILABLE_COLLECTION_PARAMS = ['page', 'sort', 'view', 'exclude-filter-info']
COLLECTION_CACHE_TIMEOUT = 60 * 15


@require_http_methods(['GET'])
def collection_view(request, slug, view='default'):
    is_ajax = request.is_ajax()

    _params = QueryDict(mutable=True)
    for k, v in request.GET.items():
        if k in AVAILABLE_COLLECTION_PARAMS:
            _params.update({k: v})

    cache_key = '%s?%s%s' % (
        request.path_info,
        _params.urlencode(),
        '|ajax' if is_ajax else '')
    result = cache.get(cache_key)
    if result:
        return result

    collection_slug, filter_chunks = split_collection_slug(slug)
    try:
        collection = Collection.objects.get(slug=collection_slug, site_id=get_current_site(request).id)
    except Collection.DoesNotExist:
        response = HttpResponseNotFound('collection not found')
        cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response

    filter_tags, vendors, prices, normalized_url_chunks, _redirect = filter_slug_to_tags(collection, filter_chunks)
    if _redirect:
        redirect_url = collection.get_absolute_url() + '/'.join(normalized_url_chunks) + '/'
        response = redirect(redirect_url)
        cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response

    ordering_type = request.GET.get('sort', pcart_settings.PCART_COLLECTION_DEFAULT_ORDERING)
    collection_view = request.GET.get('view', view)
    exclude_filter_info = request.GET.get('exclude-filter-info', False)
    page = request.GET.get('page', 1)

    template_name = settings.PCART_COLLECTION_TEMPLATES[collection_view]['template']
    paginate_by = settings.PCART_COLLECTION_TEMPLATES[collection_view]['paginate_by']

    if prices[0] or prices[1]:
        _prices = True
    else:
        _prices = False

    product_types = ProductType.objects.filter(products__collections=collection).distinct()
    properties_for_filters = ProductTypeProperty.objects.filter(
        product_type__in=product_types, use_in_filters=True)\
        .order_by('tag_prefix')\
        .values_list('title', 'tag_prefix', 'for_variants')\
        .distinct('tag_prefix')

    # Product filtering for collection

    tag_groups = regroup_tags_for_filter_sets(filter_tags)
    tags_expr = get_tags_array_query_expression(tag_groups, 'tags')
    v_tags_expr = tags_expr
    variants__tags_expr = get_tags_array_query_expression(tag_groups, 'variants__tags')

    visible_status_ids = ProductStatus.objects.filter(is_visible=True).values_list('id', flat=True)

    _products_kwargs_all = {
        'collections': collection,
        'published': True,
        'status_id__in': visible_status_ids,
    }
    _products_kwargs_without_variants = dict(_products_kwargs_all, **{'variants_count': 0})
    _variants_kwargs = {
        'product__collections': collection,
        'product__published': True,
        'status_id__in': visible_status_ids,
    }

    products = Product.objects.filter(**_products_kwargs_all)

    total_max_price = products.aggregate(Max('max_variant_price'))['max_variant_price__max']

    _filtered = False
    tag_expr_without_prices = tags_expr
    v_tag_expr_without_prices = v_tags_expr
    if _prices:
        if prices[0] and prices[1]:
            p_price_expr_ex =\
                Q(variants_count=0) & Q(price__lt=prices[0]) & Q(price__gt=prices[1])
            v_price_expr = Q(price__gte=prices[0]) & Q(price__lte=prices[1])
            variants_price_expr = Q(variants__price__gte=prices[0]) & Q(variants__price__lte=prices[1])
        elif prices[0] and prices[1] is None:
            p_price_expr_ex = Q(variants_count=0) & Q(price__lt=prices[0])
            v_price_expr = Q(price__gte=prices[0])
            variants_price_expr = Q(variants__price__gte=prices[0])
        elif prices[0] is None and prices[1]:
            p_price_expr_ex = Q(variants_count=0) & Q(price__gt=prices[1])
            v_price_expr = Q(price__lte=prices[1])
            variants_price_expr = Q(variants__price__lte=prices[1])

        _filtered = True
        tags_expr = tags_expr & ~p_price_expr_ex
        v_tags_expr = v_tags_expr & v_price_expr
        variants__tags_expr = variants__tags_expr & variants_price_expr

    if vendors:
        _filtered = True
        products = products.filter(vendor__in=vendors)

    if filter_tags:
        _filtered = True

    if _filtered:
        products = products.filter(tags_expr)
        prefetch = Prefetch(
            'variants', queryset=ProductVariant.objects.filter(v_tags_expr))
    else:
        prefetch = Prefetch('variants')

    products = products.prefetch_related(prefetch)
    products = products.prefetch_related('status')
    products = products.prefetch_related('images')
    if _filtered:
        products = products.annotate(
            filtered_variants_count=Sum(Case(
                When(variants__tags_expr, then=1),
                default=0,
                output_field=PositiveIntegerField(),
            )),
            filtered_min_variant_price=Min(Case(
                When(variants__tags_expr, then=F('variants__price')),
                default=F('max_variant_price'),
                output_field=DecimalField(),
            )),
            filtered_max_variant_price=Max(Case(
                When(variants__tags_expr, then=F('variants__price')),
                default=F('min_variant_price'),
                output_field=DecimalField(),
            )),
        )
        products = products.exclude(Q(filtered_variants_count=0) & Q(variants_count__gt=0))

    # Calculate counters for tags

    import itertools
    from collections import Counter

    nonfiltered_vendor_counters = {
        x['vendor__title']: x['id__count']
        for x in Product.objects.filter(
            **_products_kwargs_without_variants).values('vendor__title').annotate(Count('id')).order_by()}
    nonfiltered_v_vendor_counters = {
        x['product__vendor__title']: x['id__count']
        for x in ProductVariant.objects.filter(
            **_variants_kwargs).values('product__vendor__title').annotate(Count('id')).order_by()}

    filtered_vendor_counters = {
        x['vendor__title']: x['id__count']
        for x in Product.objects.filter(
            tags_expr,
            **_products_kwargs_without_variants).values('vendor__title').annotate(Count('id')).order_by()}
    filtered_v_vendor_counters = {
        x['product__vendor__title']: x['id__count']
        for x in ProductVariant.objects.filter(
            v_tags_expr,
            **_variants_kwargs).values('product__vendor__title').annotate(Count('id')).order_by()}

    vendor_counter = Counter(filtered_vendor_counters)
    v_vendor_counter = Counter(filtered_v_vendor_counters)
    t_vendor_counter = vendor_counter + v_vendor_counter

    nonfiltered_vendor_counter = Counter(nonfiltered_vendor_counters)
    nonfiltered_v_vendor_counter = Counter(nonfiltered_v_vendor_counters)
    nonfiltered_t_vendor_counter = nonfiltered_vendor_counter + nonfiltered_v_vendor_counter

    _vendors_titles = [v.title for v in vendors]
    vendor_tags = sorted([{
        'tag': t.lower(),
        'label': t,
        'count': nonfiltered_t_vendor_counter[t],
        'filtered': t_vendor_counter[t],
        'selected': t in _vendors_titles,
        'active_filter': len(_vendors_titles) > 0,
        'url': '' if t_vendor_counter[t] == 0 else collection.get_absolute_url() + '/'.join(
            normalize_filter_tags(
                collection,
                (list(vendors)+[t]) if t not in _vendors_titles else [v.title for v in vendors if v.title != t],
                prices,
                filter_tags)),
    } for t in nonfiltered_t_vendor_counter], key=lambda x: x['tag'])

    all_tags = []

    ft_groups = group_tags_for_prefixes(filter_tags)
    filter_prefixes = set([i.split(':')[0] for i in filter_tags])


    _nonfiltered_tagset = list(
        Product.objects.filter(
            **_products_kwargs_without_variants).values_list('tags', flat=True))

    _nonfiltered_v_tagset = list(ProductVariant.objects.filter(**_variants_kwargs).values_list('tags', flat=True))

    for f in properties_for_filters:
        tags_chunk = [k for k in filter_tags if k.split(':')[0] != f[1]]
        _prefix = f[1]

        tag_groups = regroup_tags_for_filter_sets(tags_chunk)
        tags_expr = get_tags_array_query_expression(tag_groups, 'tags')

        _args = [tags_expr]
        _kwargs = dict(_products_kwargs_without_variants)
        if vendors:
            _kwargs.update({'vendor__in': vendors})

        tagset = list(Product.objects.filter(*_args, **_kwargs).values_list('tags', flat=True))
        tagset = [x for x in itertools.chain(*[t for t in tagset]) if x.startswith(_prefix+':')]
        nonfiltered_tagset = [
            x for x in itertools.chain(*[t for t in _nonfiltered_tagset]) if x.startswith(_prefix + ':')]

        _args = [tags_expr]
        _kwargs = dict(_variants_kwargs)
        if vendors:
            _kwargs.update({'product__vendor__in': vendors})

        v_tagset = list(ProductVariant.objects.filter(*_args, **_kwargs).values_list('tags', flat=True))
        v_tagset = [x for x in itertools.chain(*[t for t in v_tagset]) if x.startswith(_prefix+':')]
        nonfiltered_v_tagset = [
            x for x in itertools.chain(*[t for t in _nonfiltered_v_tagset]) if x.startswith(_prefix + ':')]

        counter = Counter(tagset)
        v_counter = Counter(v_tagset)
        t_counter = counter + v_counter

        nonfiltered_counter = Counter(nonfiltered_tagset)
        nonfiltered_v_counter = Counter(nonfiltered_v_tagset)
        nonfiltered_t_counter = nonfiltered_counter + nonfiltered_v_counter

        all_tags.append({
            'group_label': f[0],
            'tags': sorted([
            {
                'tag': t,
                'label': t.split(':')[1],
                'prefix': _prefix,
                'selected': t in filter_tags,
                'active_filter': _prefix in filter_prefixes,
                'count': nonfiltered_t_counter[t],
                'url': '' if t_counter[t] == 0 else collection.get_absolute_url() + '/'.join(
                    normalize_filter_tags(
                        collection,
                        vendors,
                        prices,
                        (filter_tags+[t]) if t not in filter_tags else [x for x in filter_tags if x != t])),
                'filtered': t_counter[t],
            } for t in nonfiltered_t_counter], key=lambda x: x['tag'])})

    ordering = \
        pcart_settings.PCART_COLLECTION_ORDERINGS[ordering_type]['with_filters' if _filtered else 'without_filters']

    products = products.order_by(*ordering)

    if _filtered:
        p_agg_data = products.filter(variants_count=0).aggregate(Max('price'), Min('price'))
        v_agg_data = products.filter(variants_count__gt=0).aggregate(
            Min('filtered_min_variant_price'),
            Max('filtered_max_variant_price'),
            Sum('filtered_variants_count'),
        )
        variants_count = v_agg_data['filtered_variants_count__sum']
        min_price = min(
            [x for x in [p_agg_data['price__min'], v_agg_data['filtered_min_variant_price__min']] if x is not None] or [0])
        max_price = max(
            [x for x in [p_agg_data['price__max'], v_agg_data['filtered_max_variant_price__max']] if x is not None] or [total_max_price])

        pa_query = Product.objects.filter(tag_expr_without_prices, **_products_kwargs_without_variants)
        va_query = ProductVariant.objects.filter(
            v_tag_expr_without_prices,
            **_variants_kwargs)
        if vendors:
            pa_query = pa_query.filter(vendor__in=vendors)
            va_query = va_query.filter(product__vendor__in=vendors)
        pa_agg_data = pa_query.aggregate(Max('price'), Min('price'))
        va_agg_data = va_query.aggregate(Max('price'), Min('price'))

        min_available_price = min(
            [x for x in [pa_agg_data['price__min'], va_agg_data['price__min']] if x is not None] or [0])
        max_available_price = max(
            [x for x in [pa_agg_data['price__max'], va_agg_data['price__max']] if x is not None] or [total_max_price])
    else:
        p_agg_data = products.filter(variants_count=0).aggregate(Max('price'), Min('price'))
        v_agg_data = products.filter(variants_count__gt=0).aggregate(
            Min('min_variant_price'),
            Max('max_variant_price'),
            Sum('variants_count'),
        )
        variants_count = v_agg_data['variants_count__sum']
        min_price = min(
            [x for x in [p_agg_data['price__min'], v_agg_data['min_variant_price__min']] if x is not None] or [0])
        max_price = max(
            [x for x in [p_agg_data['price__max'], v_agg_data['max_variant_price__max']] if x is not None] or [total_max_price])

        pa_query = Product.objects.filter(**_products_kwargs_without_variants)
        va_query = ProductVariant.objects.filter(**_variants_kwargs)
        pa_agg_data = pa_query.aggregate(Max('price'), Min('price'))
        va_agg_data = va_query.aggregate(Max('price'), Min('price'))

        min_available_price = min(
            [x for x in [pa_agg_data['price__min'], va_agg_data['price__min']] if x is not None] or [0])
        max_available_price = max(
            [x for x in [pa_agg_data['price__max'], va_agg_data['price__max']] if x is not None] or [total_max_price])

    _products_list = products
    paginator = Paginator(_products_list, paginate_by)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'collection': collection,
        'filter_tags': filter_tags,
        'all_tags': all_tags,
        'vendor_tags': vendor_tags,
        'variants_count': variants_count,
        'prices': prices,
        'min_available_price': min_available_price,
        'max_available_price': max_available_price,
        'min_price': min_price,
        'max_price': max_price,
        'min_selected_price': prices[0] or min_price,
        'max_selected_price': prices[1] or max_price,
        'is_ajax': is_ajax,
        'ordering_type': ordering_type,
        'filtered': _filtered,
        'page_number': page,
        'page_url': request.path,
        'collection_view': collection_view,
    }
    response = render(request, template_name, context)
    cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
    return response


@csrf_exempt
@require_http_methods(['POST'])
def filter_form_dispatcher(request, collection_slug):
    vendors = request.POST.getlist('vendor')
    filter_tags = request.POST.getlist('tag')

    price = request.POST.get('price')
    if price is not None:
        price_from, price_to = price.split(request.POST.get('price-delimiter', ','))
    else:
        price_from = request.POST.get('price-from')
        price_to = request.POST.get('price-to')

    try:
        price_from = float(price_from)
    except ValueError:
        price_from = None
    try:
        price_to = float(price_to)
    except ValueError:
        price_to = None
    prices = (price_from, price_to)

    collection = Collection.objects.get(slug=collection_slug)
    _url = collection.get_absolute_url() + '/'.join(
        normalize_filter_tags(
            collection,
            vendors,
            prices,
            filter_tags,
        )) + '/'
    return redirect(_url)


def redirect_to_collections(request):
    return redirect('pcart_collection:all-collections')


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'catalog/product.html'

    def get_object(self, queryset=None):
        try:
            if queryset is None:
                queryset = self.model.objects.filter(published=True)
            return queryset.get(slug=self.kwargs['product_slug'])
        except Product.DoesNotExist:
            raise Http404


class ProductVariantDetailView(DetailView):
    model = ProductVariant
    context_object_name = 'variant'
    template_name = 'catalog/variant.html'

    def get_object(self, queryset=None):
        try:
            if queryset is None:
                queryset = self.model.objects.filter(product__published=True)
            return queryset.get(slug=self.kwargs['variant_slug'], product__slug=self.kwargs['product_slug'])
        except Product.DoesNotExist:
            raise Http404


def collections_list_view(request, template_name='catalog/collections.html'):
    collections = Collection.objects.filter(published=True)
    context = {
        'collections': collections,
        'page_url': request.path,
    }
    return render(request, template_name, context)
