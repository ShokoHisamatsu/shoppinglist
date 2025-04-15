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
    
    def create_superuser(self, nickname, email, password):
        user = self.create_user(
            nickname=nickname,
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
      
    
class User(AbstractBaseUser, PermissionsMixin):  
    nickname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']
    
    objects = UserManager()
    
    def get_absolute_url(self):
        return reverse_lazy('app:home')
    
    class Meta:
        app_label = 'app'
        
        
class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'store'
        
    def __str__(self):
        return self.store_name        
    
    
    
    
    
  