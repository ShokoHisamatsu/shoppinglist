from django.shortcuts import render
from .forms import UserForm


def register_view(request):
    user_form = UserForm(request.POST or None)
    return render(request, 'user/registration.html', context={
        'user_form': user_form
    })