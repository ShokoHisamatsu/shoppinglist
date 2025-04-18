from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model



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
        
User = get_user_model()
        
        
class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'store'
        
    def __str__(self):
        return self.store_name    
    
class ItemCategory(models.Model):
    item_category_name = models.CharField(max_length=100)
    
    
    class Meta:
        db_table = 'item_category'
        
    def __str__(self):
        return self.item_category_name    
    
class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    list_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lists'
        
    def __str__(self):
        return self.list_name    
    
class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    commodity = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    status = models.BooleanField(default=False)
    memo = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'list_items'
        
    def __str__(self):
        return self.commodity
    
    
    
    
    
  