from django.shortcuts import render
from django.views.generic import(
    TemplateView, CreateView, FormView, View
)
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegistForm, UserLoginForm

class HomeView(TemplateView):
    template_name = 'home.html'
    
class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('app:home')
    
class UserLoginView(FormView):
    template_name = 'user_login_form.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('app:home')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if user:
            login(self.request, user)
        return super().form_valid(form)
            
    
class UserLogoutView(View):
    pass

