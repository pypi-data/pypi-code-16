from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from .models import Review


@csrf_exempt
def review_form(request):
    from pcart_catalog.models import Product
    from pcart_customers.utils import get_customer
    site = get_current_site(request)

    product_id = request.GET.get('product-id')
    if request.method == 'POST' and 'product-id' in request.POST:
        product_id = request.POST.get('product-id')

    template_name = settings.PCART_REVIEW_FORM_TEMPLATES.get(request.GET.get('view', 'default'))
    if template_name is None:
        return HttpResponseNotFound('Unknown template.')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return HttpResponseNotFound('Product not found.')

    customer = get_customer(request, create=False)
    context = {
        'product': product,
        'customer': customer,
    }

    if request.method == 'POST':
        review = Review(
            site=site,
            product=product,
            customer=customer,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            type=request.POST.get('type', 'review'),
            pros=request.POST.get('pros', ''),
            cons=request.POST.get('cons', ''),
            comment=request.POST.get('comment'),
            rating=float(request.POST.get('rating', 2.5)),
        )
        review.save()
        context.update({'review': review})
        return render(request, 'reviews/review_thanks.html', context)

    return render(request, template_name, context)
