from django import forms
from .models import User, Store, ItemCategory, ShoppingItem, SharedList, ShoppingList, List_ItemCategory
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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
            'password': 'パスワード（8文字以上・英数字を含む）',
        }
        
        def clean(self):
            cleaned_data = super().clean()
            password1 = cleaned_data.get('password')
            password2 = cleaned_data.get('password2')

            if password1 and password2 and password1 != password2:
                self.add_error('password2', 'パスワードが一致しません')
        

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
            'store_name': 'リスト名'
        }
        widgets = {
            'store_name': forms.TextInput(
                attrs={'class': 'form-control list-name-input',
                       'placeholder': '例：スーパー、週末BBQ'
                    })
        }
        
class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        exclude = ['store']
        fields = ['item_category_name']
        labels = {
            'item_category_name': 'カテゴリ名'
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['item_category_name'].widget.attrs.update({
            'placeholder': '例）野菜・果物 など'
        })
        
    def clean_item_category_name(self):
        name = self.cleaned_data['item_category_name']
        # ✅ ログインユーザーがすでに同名カテゴリを持っていたらエラー
        if ItemCategory.objects.filter(item_category_name=name, created_by=self.user).exists():
            raise forms.ValidationError("このカテゴリはすでに存在します。")
        
        # ② 共有先リストでも使われていれば NG
        store_id = self.initial.get("store_id")  # __init__ で initial に入れておく
        if store_id:
            if List_ItemCategory.objects.filter(
                list__store__store_id=store_id,
                item_category__item_category_name=name
            ).exists():
                raise forms.ValidationError("共有中のリストで同じカテゴリ名が存在します。")
        return name
        
class CategorySelectForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=ItemCategory.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="追加するカテゴリを選んでください"
    )
    
    def __init__(self, *args, **kwargs):
        user  = kwargs.pop('user')         # ← 元々のまま
        store = kwargs.pop('store')        # ← storeも受け取るように追加！

        super().__init__(*args, **kwargs)

        # 必要に応じて store を使ってフィルタをカスタマイズ可能
        self.fields['categories'].queryset = ItemCategory.objects.filter(created_by=user)

        # store を今後使うなら self.store に保存しておいてもOK
        self.store = store
    
class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = ['commodity', 'quantity', 'memo']

        widgets={
            'commodity': forms.TextInput(attrs={'maxlength': '100', 'placeholder': '商品名'}),
            'quantity': forms.NumberInput(attrs={'min':1, 'value':1}),
            'memo': forms.TextInput(attrs={'maxlength': '100', 'placeholder': 'メモ(例：メーカーや特徴)'})
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