from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def awards_list(request):
    context = {}
    return render(request, 'awards/awards_list.html', context)
