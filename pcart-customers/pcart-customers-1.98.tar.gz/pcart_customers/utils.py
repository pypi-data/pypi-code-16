from .models import Customer


def get_customer(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
    else:
        customer = Customer.objects.get(session_id=request.session.sesion_key)
    return customer
