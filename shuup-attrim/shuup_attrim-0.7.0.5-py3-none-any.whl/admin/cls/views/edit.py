from django.forms import BaseFormSet
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from shuup.admin.toolbar import Toolbar
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm

from attrim.admin.cls.views.forms.formset import OptionFormSet
from attrim.models import Class
from attrim.helpers import get_languages_list
from attrim.helpers import get_default_lang_code


class EditClassToolbar(Toolbar):
    """
    Rewrite edit toolbar, because by default shuup won't add `delete_url`
    on it's own.
    """
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.request = view.request
        self.product = view.object
        self.extend(
            get_default_edit_toolbar(
                view_object=self.view,
                save_form_id='cls_form',
                delete_url='shuup_admin:attrim.delete',
            )
        )


class ClassForm(MultiLanguageModelForm):
    class Meta:
        model = Class
        fields = ['name', 'code', 'product_type', 'type']
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Disabled editing of `type` field on an existing instance,
        # or user may screw it up.
        if self.is_bound:
            self.fields['type'].required = False
            self.fields['type'].widget.attrs['disabled'] = 'disabled'


class ClassEditView(CreateOrUpdateView):
    model = Class
    form_class = ClassForm
    template_name = 'attrim/admin/cls/edit.jinja'
    context_object_name = 'attribute'
    #: it will be the model instance
    object = None

    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        response_redirect = super().post(request, *args, **kwargs)

        if self.is_cls_form_valid():
            cls_obj = self.object
            cls_obj.save()

            option_formset = OptionFormSet(
                self.request.POST,
                cls=cls_obj,
            )
            if option_formset.is_valid():
                option_formset.save()

        return response_redirect

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context['option_formset'] = self.get_option_formset()
        
        # used by typescript for options formset handling
        context['languages_list'] = get_languages_list()
        context['DEFAULT_LANG_CODE'] = get_default_lang_code()

        context['title'] = _('New attribute class')

        return context

    def get_toolbar(self) -> EditClassToolbar:
        return EditClassToolbar(view=self)

    def get_option_formset(self) -> BaseFormSet:
        cls_obj = self.object
        return OptionFormSet(
            cls=cls_obj,
            initial=cls_obj.get_initial_data_for_form(),
        )

    def is_cls_form_valid(self):
        cls_from = self.get_form()
        if cls_from.is_valid:
            return True
        else:
            return False
