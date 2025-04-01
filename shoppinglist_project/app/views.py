from django.shortcuts import render
from django.views.generic import(
    TemplateView, CreateView, FormView
)


class HomeView(TemplateView):
    template_name = 'home.html'
    
class RegistUserView(CreateView):
    template_name = ' regist.html'
    form_class = RegistForm