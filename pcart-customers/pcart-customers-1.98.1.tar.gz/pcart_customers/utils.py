from .models import Customer


def get_customer(request, create=True):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
    else:
        try:
            customer = Customer.objects.get(session_id=request.session.session_key)
        except Customer.DoesNotExist:
            if create:
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                customer = Customer.objects.create(session_id=request.session.session_key)
                request.session['customer_id'] = str(customer.id)
            else:
                customer = None
    return customer
