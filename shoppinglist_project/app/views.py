from django.shortcuts import render
from django.views.generic import(
    TemplateView, CreateView, FormView, View
)
from django.urls import reverse_lazy
from .forms import RegistForm

class HomeView(TemplateView):
    template_name = 'home.html'
    
class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('app:home')
    
class UserLoginView(FormView):
    template_name = 'user_login.html'
    
class UserLogoutView(View):
    pass

