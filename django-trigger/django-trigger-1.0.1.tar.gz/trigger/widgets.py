from django import forms
from django.template.loader import render_to_string


class RepeatWidget(forms.Widget):

    def __init__(self, attrs=None, choices=()):
        super(RepeatWidget, self).__init__(attrs)
        self.choices = choices
    # end def

    def render(self, name, value, attrs=None, choices=()):
        dias = range(0, 7)
        mes = range(1, 31)
        return render_to_string("notificaciones/repeat.html", {'name': name, 'value': value, 'choices': self.choices, 'dias': dias, 'mes':mes})
    # end def

    class Media:
        css = {
            'all': ('notificaciones/css/repeat.css', )
        }
        js = ('notificaciones/js/repeat.js', )
    # end class

# end class


class IntervalWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        dias = range(0, 7)
        mes = range(1, 31)
        return render_to_string("notificaciones/interval.html", {'name': name, 'value': value, 'dias': dias, 'mes':mes})
    # end def

    class Media:
        css = {
            'all': ('notificaciones/css/interval.css',)
        }
        js = ('notificaciones/js/interval.js',)
    # end class

# end class
