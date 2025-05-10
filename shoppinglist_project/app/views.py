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
from secrets import token_urlsafe


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_list'] = Store.objects.filter(created_by=self.request.user)
        context['form'] = StoreForm()
        return context

    def post(self, request, *args, **kwargs):
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.created_by = request.user 
            store.save()
            messages.success(request, 'お店を追加しました。')
            return redirect('app:home')
        else:
            messages.error(request, 'お店の追加に失敗しました。')
            return self.get(request, *args, **kwargs)
    
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
        category_id_map = {}
        for linked in linked_categories:
            category = linked.item_category
            items = ShoppingItem.objects.filter(
                shopping_list=shopping_list,
                item_category=category
            )
            category_item_map[category] = items
            category_id_map[category] = linked
        
        context = {
            'store': store,
            'category_item_map' : category_item_map,
            'category_id_map': category_id_map,
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
    
@login_required
def category_delete(request, pk):
    list_category = get_object_or_404(List_ItemCategory, pk=pk)

    # 安全確認：ログインユーザーのリストに紐づいてるか
    if list_category.list.user != request.user:
        return redirect('app:home')

    # 紐づくアイテムを削除
    ShoppingItem.objects.filter(
        shopping_list=list_category.list,
        item_category=list_category.item_category
    ).delete()

    # リンク自体を削除
    list_category.delete()

    return redirect('app:mylist', store_id=list_category.list.store.store_id)
    
    
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
    template_name = 'shared/shared_list_fix.html'
    form_class = SharedListForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs.get('store_id')
        user = self.request.user
        store = get_object_or_404(Store, store_id=store_id, created_by=user)

        shopping_list, _ = ShoppingList.objects.get_or_create(
            store=store,
            user=user,
            defaults={'list_name': f'{store.store_name}のリスト'}
        )

        shared_list = SharedList.objects.filter(list=shopping_list, created_by=user).first()

        shared_list, created = SharedList.objects.get_or_create(
        list=shopping_list,
        created_by=user,
        defaults={'url_token': secrets.token_urlsafe(8)}
        )

        share_url = self.request.build_absolute_uri(
            reverse('app:shared_list_detail', args=[shared_list.url_token])
        )

        context.update({
            'store': store,
            'shopping_list': shopping_list,
            'shared_list': shared_list,
            'share_url': share_url,
            'form': self.get_form(),
        })
        return context

    def post(self, request, *args, **kwargs):
        store_id = self.kwargs.get('store_id')
        user = request.user
        store = get_object_or_404(Store, store_id=store_id, created_by=user)

        shopping_list, _ = ShoppingList.objects.get_or_create(
            store=store,
            user=user,
            defaults={'list_name': f'{store.store_name}のリスト'}
        )

        if 'delete_shared_list' in request.POST:
            SharedList.objects.filter(list=shopping_list, created_by=user).delete()
            messages.success(request, f"{store.store_name}の共有を解除しました。")
            return redirect('app:shared_list_create', store_id=store_id)

        shared_list, created = SharedList.objects.get_or_create(
            list=shopping_list,
            created_by=user,
            defaults={
                'url_token': secrets.token_urlsafe(8),
            }
        )

        messages.success(request, f"{store.store_name}の共有設定を更新しました。")
        return redirect('app:shared_list_create', store_id=store_id)


    
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
        all_stores = Store.objects.filter(created_by=self.request.user).distinct()
        shared_lists = SharedList.objects.filter(created_by=self.request.user)  
        shared_store_ids = shared_lists.values_list('list__store__store_id', flat=True)  
        
        shared_stores = all_stores.filter(store_id__in=shared_store_ids)
        unshared_stores = all_stores.exclude(store_id__in=shared_store_ids)

        context['stores'] = shared_stores
        context['unshared_stores'] = unshared_stores
        return context

    def post(self, request, *args, **kwargs):
        shared_list_ids = request.POST.getlist('shared_lists')
        if shared_list_ids:
            SharedList.objects.filter(id__in=shared_list_ids, created_by=request.user).delete()
            messages.success(request, "選択した共有を解除しました。")
        else:
            messages.warning(request, "共有を選択してください。")
        return redirect('app:shared_list_manage')
    
    
class SharedListAddView(LoginRequiredMixin, View):
    def post(self, request):
        store_id = request.POST.get('store_id')
        
        if store_id:
            try:
                store = Store.objects.get(pk=store_id)  
                
                if not SharedList.objects.filter(list__store=store, created_by=request.user).exists():
                    shopping_list = ShoppingList.objects.get(store=store, user=request.user)
                    SharedList.objects.create(list=shopping_list, created_by=request.user, url_token=token_urlsafe(8))
                    messages.success(request, f"{store.store_name}を共有リストに追加しました。")
                else:
                    messages.success(request, f"{store.store_name}は既に追加されています。")
                    
            except Store.DoesNotExist:
                messages.error(request, "対象のお店が見つかりません。")
            except ShoppingList.DoesNotExist:
                messages.error(request, "対象のショッピングリストが見つかりません。")
                
        return redirect('app:shared_list_manage')                  

    