from shuup.apps import AppConfig as ShuupAppConfig


class AppConfig(ShuupAppConfig):
    name = 'attrim'
    verbose_name = 'Attrim'
    label = 'attrim'
    provides = {
        'admin_module': [
            'attrim.admin.cls.main:ClassModule',
        ],
        'admin_product_form_part': [
            'attrim.admin.product.forms:AttributesFormPart',
        ],
    }
