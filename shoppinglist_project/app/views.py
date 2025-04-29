from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import(
    TemplateView, CreateView, FormView, View, DeleteView, UpdateView,
    DetailView, ListView
)
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect
from .forms import (
    RegistForm, UserLoginForm, StoreForm, ItemCategoryForm, 
    CategorySelectForm, ShoppingItemForm, EmailChangeForm, SharedListForm,
    SharedListBulkDeleteForm
)
from .models import Store, ItemCategory, ShoppingItem, ShoppingList, List_ItemCategory, User, SharedList
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import secrets


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
        store = get_object_or_404(Store, store_id=store_id)
        shopping_list =ShoppingList.objects.filter(
            store=store, user=request.user
            ).first()
        
        linked_categories = List_ItemCategory.objects.filter(
            list=shopping_list
        ).select_related('item_category')
        
        category_item_map = {}
        for linked in linked_categories:
            category = linked.item_category
            items = ShoppingItem.objects.filter(
                shopping_list=shopping_list,
                item_category=category
            )
            category_item_map[category] = items
        
        context = {
            'store': store,
            'category_item_map' : category_item_map,
            'shopping_list' : shopping_list,
            'form': ShoppingItemForm()
        }
        return self.render_to_response(context)
    
    def post(self, request,store_id, *args, **kwargs):
        store = get_object_or_404(Store, store_id=store_id)
        shopping_list = ShoppingList.objects.filter(
            store=store, user=request.user
        ).first()
        
        form = ShoppingItemForm(request.POST)
        
        if form.is_valid():
            category_id = request.POST.get('category_id')
            category = get_object_or_404(ItemCategory, id=category_id)
            
            item = form.save(commit=False)
            item.shopping_list = shopping_list
            item.item_category = category
            item.save()
            
        return redirect('app:mylist', store_id=store.store_id)
            
    
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
        return reverse_lazy('app:category_add', kwargs={'store_id': store_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs['store_id']
        store = get_object_or_404(Store, store_id=store_id)
        context["store"] = store 
        return context
    
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
    
class CategoryAddView(FormView):
    template_name = 'category_add.html'
    form_class = CategorySelectForm
    
    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       store = get_object_or_404(Store, store_id=self.kwargs['store_id'])
       context["store"] = store
       return context
    
    def form_valid(self, form):
        store = get_object_or_404(Store, store_id=self.kwargs['store_id'])
        
        shopping_list, created = ShoppingList.objects.get_or_create(
            store=store, 
            user=self.request.user,
            defaults={
                'list_name': f'{store.store_name}のリスト'
            }
        )
        
        categories = form.cleaned_data['categories']
        
        for category in categories:
            List_ItemCategory.objects.get_or_create(
                list=shopping_list,
                item_category=category,
            )
    
        return redirect('app:mylist', store_id=store.store_id)
    
    
class ItemCheckView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ShoppingItem, id=item_id)
        item.status = not item.status
        item.save()
        return redirect('app:mylist', store_id=item.shopping_list.store.store_id)
    
class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = ShoppingItem
    template_name = 'item_delete.html'
    
    def get_success_url(self):
        store_id = self.object.shopping_list.store.store_id
        return reverse_lazy('app:mylist', kwargs={'store_id': store_id})
    
class EmailChangeView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EmailChangeForm
    template_name = 'email_change.html'
    success_url = reverse_lazy('app:email_change_done')
    
    def get_object(self, queryset=None):
        return self.request.user
    
class SharedListCreateView(LoginRequiredMixin, FormView):
    template_name = 'shared_list_form.html'
    form_class = SharedListForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs.get('store_id')
        user = self.request.user
        try:
            shared_list = SharedList.objects.get(list__store_id=store_id, created_by=user)
            share_url = self.request.build_absolute_uri(
                reverse('app:shared_list_detail', args=[shared_list.url_token])
            )
        except SharedList.DoesNotExist:
            share_url = None
        context['share_url'] = share_url
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        store_id = self.kwargs['store_id']
        store_list_instance = ShoppingList.objects.get(store_id=store_id, user=self.request.user)
        kwargs['store_list_instance'] = store_list_instance
        return kwargs

    def form_valid(self, form):
        store_id = self.kwargs.get('store_id')
        user = self.request.user
        
        shopping_list = ShoppingList.objects.get(store_id=store_id, user=user)

        shared_list, created = SharedList.objects.get_or_create(
            list=shopping_list,
            created_by=user,
            defaults={
                'url_token': secrets.token_urlsafe(8),
                'can_edit': form.cleaned_data['can_edit'], 
            }
        )
        
        if not created:
            shared_list.can_edit = form.cleaned_data['can_edit']
            shared_list.save()

        share_url = self.request.build_absolute_uri(
            reverse('app:shared_list_detail', args=[shared_list.url_token])
        )
        messages.success(self.request, f"{shopping_list.store.store_name}共有URLを作成しました。")
        return render(self.request, self.template_name, {
            'form': form,  
            'share_url': share_url,
            'can_edit': form.cleaned_data['can_edit'],
        })
        
    def form_invalid(self, form):
        messages.error(self.request, "フォームにエラーがあります。")
        return super().form_invalid(form) 

    
class SharedListDetailView(DetailView):
    model = SharedList
    template_name = 'shared/shared_list_detail.html'
    context_object_name = 'shared_list'
    slug_field = 'url_token'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shopping_list = self.object.list

        linked_categories = List_ItemCategory.objects.filter(
            list=shopping_list
        ).select_related('item_category')

        category_item_map = {}
        for linked in linked_categories:
            category = linked.item_category
            items = ShoppingItem.objects.filter(
                shopping_list=shopping_list,
                item_category=category
            )
            category_item_map[category] = items

        context['shopping_list'] = shopping_list
        context['category_item_map'] = category_item_map
        context['can_edit'] = self.object.can_edit
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  
        if not self.object.can_edit:
            return HttpResponseForbidden("このリストは編集できません")

        shopping_list = self.object.list
        
        if 'check_item_id' in request.POST:
            from .models import ShoppingItem
            item_id = request.POST['check_item_id']
            item = get_object_or_404(ShoppingItem, id=item_id, shopping_list=shopping_list)
            item.status = not item.status
            item.save()
        elif 'commodity' in request.POST:
            form = ShoppingItemForm(request.POST)
            if form.is_valid():
                category_id = request.POST.get('category_id')
                from .models import ItemCategory
                category = get_object_or_404(ItemCategory, id=category_id)
                item = form.save(commit=False)
                item.shopping_list = shopping_list
                item.item_category = category
                item.save()

        return redirect('app:shared_list_detail', uuid=self.object.url_token)
    
class SharedListManageView(LoginRequiredMixin, TemplateView):
    template_name = 'shared/shared_list_manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stores'] = ShoppingList.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        shared_list_ids = request.POST.getlist('shared_lists')
        if shared_list_ids:
            SharedList.objects.filter(id__in=shared_list_ids, created_by=request.user).delete()
            messages.success(request, "選択した共有を解除しました。")
        else:
            messages.warning(request, "共有を選択してください。")
        return redirect('app:shared_list_manage')
    
class SharedListDeleteView(View):
    def post(self, request, *args, **kwargs):
        shared_list_ids = request.POST.getlist('shared_lists')

        if shared_list_ids:
            SharedList.objects.filter(id__in=shared_list_ids).delete()
            messages.success(request, "選択した共有を解除しました。")
        else:
            messages.warning(request, "共有解除するリストが選択されていません。")

        return HttpResponseRedirect(reverse('app:shared_list_manage'))

    