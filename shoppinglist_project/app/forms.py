from django import forms
from .models import User
from django.contrib.auth.password_validation import validate_password

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
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())