from __future__ import absolute_import

import json

from django.http.response import HttpResponse, HttpResponseBadRequest, Http404, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.generic.base import View

from rapidprototype.core.default_settings import SITE_PAGES_DIRECTORY
from rapidprototype.forms import PlaceHolderImageForm
from rapidprototype.utils import _get_node


class PlaceHolderImageView(View):
    height = 100
    width = 100

    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        form = PlaceHolderImageForm({'height': kwargs.get('height', self.height),
                                     'width': kwargs.get('width', self.width)})
        if form.is_valid():
            image = form.generate(text=kwargs.get('text', None), color_string=request.GET.get('color_string', None))
            return HttpResponse(image, content_type='image/png')
        else:
            return HttpResponseBadRequest('Invalid image request')

placeholder_image_view = PlaceHolderImageView.as_view()


class StaticPagesView(View):
    http_method_names = ['get', ]

    def get_page_or_404(self, name):
        """
        :param name: name of the template to be rendered
        :return: file_path after validation
        """
        try:
            template_string = '{}/{}'.format(SITE_PAGES_DIRECTORY, name)
            template = get_template(template_string)
        except:
            raise Http404('Page not found')

        try:
            self._context = _get_node(template.template, name='context')
        except Exception as e:
            self._context = None


        return template_string

    def dispatch(self, request, *args, **kwargs):
        self.slug = kwargs.get('slug', 'index')
        self.file_name = '{}.html'.format(self.slug)
        self.page = self.get_page_or_404(self.file_name)
        return super(StaticPagesView, self).dispatch(request, *args, **kwargs)

    def get_context(self, **kwargs):
        context = {
            'slug': self.slug,
            'page': self.page,
        }
        if self._context != None:
            extra_content = json.loads(self._context)
            context.update(extra_content)

        context.update(kwargs)

        return context

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return JsonResponse(data=self.get_context(), safe=False)
        return render(request, self.page, self.get_context())

static_pages_view = StaticPagesView.as_view()