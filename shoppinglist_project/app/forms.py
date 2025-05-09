from django import forms
from .models import User, Store, ItemCategory, ShoppingItem, SharedList, ShoppingList
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistForm(forms.ModelForm):
    password2 = forms.CharField(
        label= "パスワード再入力",
        widget=forms.PasswordInput(),
    )
    
    class Meta:
        model = User
        fields = ['nickname', 'email', 'password']
        widgets = {
            'password' : forms.PasswordInput(),
        }
        labels = {
            'nickname': 'ニックネーム',
            'email': 'メールアドレス',
            'password': 'パスワード',
        }
        

    def save(self, commit=False):
         user = super().save(commit=False)
         validate_password(self.cleaned_data['password'], user)
         user.set_password(self.cleaned_data['password'])
         user.save()
         return user
     
class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス (半角英数)')
    password = forms.CharField(label='パスワード(半角6文字以上)', widget=forms.PasswordInput())
    
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['store_name']
        labels = {
            'store_name': '店舗名'
        }
        
class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        exclude = ['store']
        fields = ['item_category_name']
        labels = {
            'item_category_name': 'カテゴリ名'
        }
        
class CategorySelectForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=ItemCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="追加するカテゴリを選んでください"
    )
    
class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = ['commodity', 'quantity', 'memo']

        widgets={
            'commodity': forms.TextInput(attrs={'placeholder': '商品名'}),
            'quantity': forms.NumberInput(attrs={'min':1, 'value':1}),
            'memo': forms.TextInput(attrs={'placeholder': 'メモ(例：メーカーや特徴)'})
        }
        
class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        labels = {
            'email': '新しいメールアドレス'
        }
        
class SharedListForm(forms.ModelForm):
    class Meta:
        model = SharedList
        fields = ['can_edit']
        labels = {
            'list' : '共有するリスト',
            'can_edit' : '編集権限を付与しますか？'
        }  
        
    def __init__(self, *args, **kwargs):
        store_list_instance = kwargs.pop('store_list_instance', None)
        super().__init__(*args, **kwargs)
        
        if store_list_instance:
            self.instance.list = store_list_instance 

class SharedListBulkDeleteForm(forms.Form):
    shared_lists = forms.ModelMultipleChoiceField(
        queryset=SharedList.objects.none(), 
        widget=forms.CheckboxSelectMultiple,
        label='どの共有をやめますか？'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['shared_lists'].queryset = SharedList.objects.filter(created_by=user)