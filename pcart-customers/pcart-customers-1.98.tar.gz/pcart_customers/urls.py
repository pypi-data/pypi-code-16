from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .forms import UserPasswordResetForm
from . import views


urlpatterns = [
    url(
        r'^login/$', auth_views.login,
        {'template_name': 'customers/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    # url(
    #     r'^register/$', register_view,
    #     name='register'),
    # url(r'^register/success/$',
    #     TemplateView.as_view(
    #         template_name='accounts/registration_success.html'),
    #     name='registration_success'),
    url(
        r'^password-change/$',
        auth_views.password_change,
        {
            'template_name': 'customers/password_change_form.html',
            'post_change_redirect': 'pcart_customers:password-change-done',
        },
        name='password-change'),
    url(
        r'^password-change/done/$',
        auth_views.password_change_done,
        {'template_name': 'customers/password_change_done.html'},
        name='password-change-done'),
    url(
        r'^password-reset/$',
        auth_views.password_reset,
        {
            'template_name': 'customers/password_reset_form.html',
            'password_reset_form': UserPasswordResetForm},
        name='password_reset'),
    url(
        r'^password-reset/done/$',
        auth_views.password_reset_done,
        {'template_name': 'customers/password_reset_done.html'},
        name='password_reset_done'),
    url(
        r'^password-reset/(?P<uidb64>.+)/(?P<token>.+)/confirm/$',
        auth_views.password_reset_confirm,
        {'template_name': 'customers/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(
        r'^password-reset/complete/$',
        auth_views.password_reset_complete,
        {'template_name': 'customers/password_reset_complete.html'},
        name='password_reset_complete'),

    url(r'^personal-information/$', views.personal_information, name='personal-information'),
    url(r'^customer-toolbar/$', views.customer_toolbar, name='customer-toolbar'),
    url(r'^(?P<slug>[\w\d-]+)/$', views.profile_section, name='customer-profile-section'),
]
