from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
        
class UserManager(BaseUserManager):
    def create_user(self, nickname, email, password):
        if not email:
            raise ValueError('Emailアドレスを入力してください')
        if not password:
            raise ValueError('パスワードを入力してください')
        user = self.model(
            nickname=nickname,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user
    
    
class User(AbstractBaseUser, PermissionsMixin):  
    nickname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()
    
    def get_absolute_url(self):
        return reverse_lazy('app:home')
    
    
    
    
    
  