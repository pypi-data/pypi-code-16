from django.apps import apps
from django.contrib import admin, messages
from django.contrib.admin.sites import AlreadyRegistered
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.utils.translation import ugettext as _

from . import models


# TODO: Add an action to populate generic types.


class VatInline(admin.TabularInline):
    model = models.Vat
    fields = (
        'vat_type',
        'base_amount',
        'amount',
    )
    extra = 1


class TaxInline(admin.TabularInline):
    model = models.Tax
    fields = (
        'tax_type',
        'description',
        'base_amount',
        'aliquot',
        'amount',
    )
    extra = 1


class ReceiptStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'status'

    VALIDATED = 'validated'
    NOT_VALIDATED = 'not_validated'

    def lookups(self, request, model_admin):
        return (
            (self.VALIDATED, _('Validated')),
            (self.NOT_VALIDATED, _('Not validated')),
        )

    def queryset(self, request, queryset):
        if self.value() == self.VALIDATED:
            return queryset.filter(
                validation__result=models.Validation.RESULT_APPROVED
            )
        if self.value() == self.NOT_VALIDATED:
            return queryset.exclude(
                validation__result=models.Validation.RESULT_APPROVED
            )


class ReceiptBatchedFilter(admin.SimpleListFilter):
    title = _('batched')
    parameter_name = 'batched'

    BATCHED = 'batched'
    NOT_BATCHED = 'not_batched'

    def lookups(self, request, model_admin):
        return (
            (self.BATCHED, _('Batched')),
            (self.NOT_BATCHED, _('Not batched')),
        )

    def queryset(self, request, queryset):
        if self.value() == self.BATCHED:
            return queryset.filter(
                batch__isnull=True,
            )
        if self.value() == self.NOT_BATCHED:
            return queryset.filter(
                batch__isnull=False
            )


class ReceiptAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'receipt_type',
        'point_of_sales',
        'receipt_number',
        'issued_date',
        'total_amount',
        'batch_link',
        'validated',
    )
    list_filter = (
        ReceiptBatchedFilter,
        ReceiptStatusFilter,
        'batch',
    )

    __related_fields = [
        'validated',
        'cae',
    ]

    filter_horizontal = ('related_receipts',)

    inlines = (
        VatInline,
        TaxInline,
    )
    ordering = (
        'id',
    )

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)

    readonly_fields = __related_fields

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .select_related(
                'validation',
                'receipt_type',
                'point_of_sales',
                'batch',
            )

    def validated(self, obj):
        return obj.validation.result == models.Validation.RESULT_APPROVED
    validated.short_description = _('validated')
    validated.admin_order_field = 'validation__result'
    validated.boolean = True

    def cae(self, obj):
        return obj.validation.cae
    cae.short_description = _('cae')
    cae.admin_order_field = 'validation__cae'

    def create_batch(self, request, queryset):
        variations = queryset \
            .aggregate(
                receipt_types=Count('receipt_type', distinct=True),
                points_of_sales=Count('point_of_sales', distinct=True),
            )

        if variations['receipt_types'] > 1:
            self.message_user(
                request,
                _(
                    'The selected receipts are not all of the same type.'
                ),
                messages.ERROR,
            )
            return
        if variations['points_of_sales'] > 1:
            self.message_user(
                request,
                _(
                    'The selected receipts are not all from the same point '
                    'of sales.'
                ),
                messages.ERROR,
            )
            return

        queryset = queryset.filter(batch__isnull=True)
        if not queryset.count():
            self.message_user(
                request,
                _('All the selected invoices have already been batched'),
                messages.ERROR,
            )
            return

        models.ReceiptBatch.objects.create(queryset)
        # TODO: Maybe redirect to batch screen?
    create_batch.short_description = _('Create receipt batch')

    def batch_link(self, obj):
        if not obj.batch:
            return None
        return '<a href="{}">{}</a>'.format(
            reverse('admin:afip_receiptbatch_change', args=(obj.batch.id,)),
            obj.batch.id
        )
    batch_link.admin_order_field = 'batch'
    batch_link.allow_tags = True
    batch_link.short_description = _('batch')

    actions = [create_batch]


class ReceiptBatchAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'receipts_count',
        'validated',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            Count('receipts', distinct=True)
        )

    def validated(self, obj):
        return obj.validation \
            .filter(result=models.Validation.RESULT_APPROVED) \
            .count() > 0
    validated.short_description = _('validated')
    validated.admin_order_field = 'validation__result'
    validated.boolean = True

    def receipts_count(self, obj):
        return '<a href="{}?batch__id__exact={}">{}</a>'.format(
            reverse(self.admin_site.name + ':afip_receipt_changelist'),
            obj.id,
            obj.receipts__count,
        )
    receipts_count.allow_tags = True
    receipts_count.short_description = _('receipts')
    receipts_count.admin_order_field = 'receipts__count'

    def validate(self, request, queryset):
        for batch in queryset:
            errs = batch.validate()
            if errs:
                self.message_user(
                    request,
                    _(
                        'Batch #%(num)s failed: %(err)s'
                    ) % {'num': batch.pk, 'err': errs},
                    messages.ERROR,
                )
    validate.short_description = _('Validate')

    actions = [validate]


class AuthTicketAdmin(admin.ModelAdmin):
    list_display = (
        'unique_id',
        'owner',
        'service',
        'generated',
        'expires',
    )


class TaxPayerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cuit',
    )

    def fetch_points_of_sales(self, request, queryset):
        poses = [
            pos
            for taxpayer in queryset.all()
            for pos in taxpayer.fetch_points_of_sales()
        ]

        created = len([pos for pos in poses if pos[1]])
        total = len(poses)

        self.message_user(
            request,
            message=(
                _(
                    '%(total)d points of sales fetched. %(created)d created.'
                ) % dict(
                    total=total,
                    created=created,
                )
            ),
            level=messages.SUCCESS,
        )

    fetch_points_of_sales.short_description = _('Fetch points of sales')

    actions = (
        fetch_points_of_sales,
    )


@admin.register(models.PointOfSales)
class PointOfSalesAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'number',
        'issuance_type',
        'blocked',
        'drop_date',
    )


admin.site.register(models.Receipt, ReceiptAdmin)
admin.site.register(models.ReceiptBatch, ReceiptBatchAdmin)
admin.site.register(models.AuthTicket, AuthTicketAdmin)
admin.site.register(models.TaxPayer, TaxPayerAdmin)

app = apps.get_app_config('afip')
for model in app.get_models():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
