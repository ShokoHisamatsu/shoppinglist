from django.shortcuts import render, redirect
from django.views.generic import(
    TemplateView, CreateView, FormView, View, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegistForm, UserLoginForm, StoreForm, ItemCategoryForm
from .models import Store, ItemCategory, ShoppingItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


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
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else self.success_url            
    
class UserLogoutView(View):
    def get(self, request, *args,**kwargs):
        return render(request, 'user_logout_form.html')

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('app:home')
    
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['store_list'] = Store.objects.all()
        context['form'] = StoreForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:home')
        context = self.get_context_data()
        return self.render_to_response(context)

class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    success_url = reverse_lazy('app:home')
    template_name = 'store_confirm_delete.html'
        
    
    
class MyListView(LoginRequiredMixin, TemplateView):
    template_name = 'mylist.html'
    
    def get(self, request, store_id,  *args, **kwargs):
        store = Store.objects.get(store_id=store_id)
        categories = ItemCategory.objects.all()
        
        category_item_map = {}
        for category in categories:
            items = ShoppingItem.objects.filter(
                shopping_list__store=store,
                item_category=category
            )
            category_item_map[category] = items
        
        context = {
            'store': store,
            'category_item_map' : category_item_map,
        }
        return self.render_to_response(context)
    
class CategoryListView(TemplateView):
    template_name='category_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs.get('store_id')
        
        store = Store.objects.get(store_id=store_id)
        categories = ItemCategory.objects.all()
        
        context['store'] = store
        context['categories'] = categories
        return context
    
class ItemCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ItemCategory
    form_class = ItemCategoryForm
    template_name = 'itemcategory_form.html'
    
    def get_success_url(self):
        store_id = self.kwargs['store_id']
        return reverse_lazy('app:category_list', kwargs={'store_id': store_id})
    
class CategoryItemListView(TemplateView):
    template_name='category_item_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs.get('store_id')
        category_id = self.kwargs.get('category_id')
        
        store = Store.objects.get(store_id=store_id)
        category = ItemCategory.objects.get(id=category_id)
        items = ShoppingItem.objects.filter(shopping_list__store=store, item_category=category)
        
        context['store'] = store
        context['category'] = category
        context['items'] = items
        return context
    
    