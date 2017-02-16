from django.shortcuts import render

# Create your views here.
from django.views.generic.base import TemplateView


class PlaceholderImageExampleView(TemplateView):
    template_name = 'placeholder/placeholder_example.html'

placeholder_image_example_view = PlaceholderImageExampleView.as_view()
