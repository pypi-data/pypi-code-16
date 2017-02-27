from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def reviews_for_product(context, product, review_type='all', template='default'):
    from ..models import Review
    reviews = Review.objects.filter(product=product, status='published')
    if review_type != 'all':
        reviews = reviews.filter(type=review_type)
    new_context = {
        'product': product,
        'reviews': reviews,
    }
    template_name = settings.PCART_REVIEWS_THREAD_TEMPLATES[template]
    return mark_safe(render_to_string(template_name, new_context, context['request']))
