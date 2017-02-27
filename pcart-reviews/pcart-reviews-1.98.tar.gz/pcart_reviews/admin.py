from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import Review


class ReviewAdmin(MPTTModelAdmin):
    list_display = ('review', 'site', 'rating', 'added', 'status')
    date_hierarchy = 'added'
    search_fields = ('comment', 'name', 'email', 'pros', 'cons', 'product')
    raw_id_fields = ('product', 'product_variant', 'customer', 'parent')
    list_filter = ('status', 'site')
    list_display_links = None

    def review(self, obj):
        HTML = '''<div>
<div><a href="{review_url}">{pros}/{cons}</a>
<span style="float:right;">[{type}]</span></div>
<div>{comment}</div>
<div>- <a href="{customer_url}">{customer}</a> on
<a href="{product_url}">{product_title}</a></div>
</div>
        '''
        return format_html(
            HTML,
            review_url=reverse('admin:pcart_reviews_review_change', args=(obj.id,)),
            product_title=obj.product.title,
            type=obj.type,
            pros=obj.pros,
            cons=obj.cons,
            comment=obj.comment,
            product_url=reverse('admin:pcart_catalog_product_change', args=(obj.product_id,)),
            customer_url=reverse('admin:pcart_customers_customer_change', args=(obj.customer_id,)),
            customer=obj.name,
        )
    review.short_description = _('Review')


admin.site.register(Review, ReviewAdmin)
