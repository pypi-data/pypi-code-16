from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from .forms import StartForm
from .models import Users

# Create your views here.

def start(request):
    if request.method == 'POST':
        start_form = StartForm(request.POST)
        if start_form.is_valid():
            data = start_form.save(commit=False)
            # user_object = Users.objects.get(username=data.username)
            try:
                # user_object = get_object_or_404(Users, username=data.username)
                user_object = Users.objects.get(username=data.username)
            except Users.DoesNotExist:
                return render(request, 'simpleauth/fourohfour.html', {'user' : data.username, 'title' : 'BAD USER'})
            if data.password == user_object.password:
                users = Users.objects.values('username')
                return render(request, 'simpleauth/inside.html', {'users' : users})
            else:
                msg = 'INVALID LOGIN ! PLEASE CHECK !'
                return render(request, 'simpleauth/outside.html', {'msg' : msg, 'title' : 'Invalid User'})
    else:
        start_form = StartForm()
    return render(request, 'simpleauth/index.html', {'start_form' : start_form})


def register(request):
    if request.method == 'POST':
        reg_form = StartForm(request.POST)
        if reg_form.is_valid():
            reg_form.save(commit=True)
#             data = reg_form.save(commit=False)
#             Users.objects.create(username=data.username, password=data.password)
            return render(request, 'simpleauth/thanks.html', {})
    else:
        reg_form = StartForm()
    return render(request, 'simpleauth/register.html', {'reg_form' : reg_form})
