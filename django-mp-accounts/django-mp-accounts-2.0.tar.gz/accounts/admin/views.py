
from django.shortcuts import render
from django.contrib.auth import get_user_model


def user_statistic(request):

    request.current_app = 'accounts'

    users = get_user_model().objects.all()

    context = {
        'all_users_count': len(users),
        'active_users_count': len(users.filter(is_active=True)),
        'inactive_users_count': len(users.filter(is_active=False)),
        'staff_users_count': len(users.filter(is_staff=True))
    }

    return render(request, 'account/admin/statistic.html', context)
