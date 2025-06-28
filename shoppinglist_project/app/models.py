from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractBaseUser, PermissionsMixin, User
)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
import uuid
from .utils import generate_token
      
        
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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store'
        
    def __str__(self):
        return self.store_name    
    
class ItemCategory(models.Model):
    item_category_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'item_category'
        constraints = [
    models.UniqueConstraint(
        fields=["item_category_name", "created_by"],
        name="unique_category_per_user"
    )
]
        
    def __str__(self):
        return self.item_category_name    
    
class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shoppinglist_user')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='shoppinglist_store')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shoppinglist_creator')
    list_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        db_table = 'lists'
        constraints = [                   
            models.UniqueConstraint(
                fields=['store'],         
                name='unique_store'       
            )
        ]
        
    def __str__(self):
        return self.list_name
    
class List_ItemCategory(models.Model):
    list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name='linked_lists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'list_itemcategory'
        
    def __str__(self):
        return f'{self.list} - {self.item_category}'
           
    
class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    commodity = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    status = models.BooleanField(default=False)
    memo = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_checked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'list_items'
        
    def __str__(self):
        return self.commodity
    
class SharedList(models.Model):
    list = models.OneToOneField(ShoppingList, on_delete=models.CASCADE)
    url_token = models.CharField(max_length=255, unique=True, editable=False)
    can_edit = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(User, related_name='shared_lists', blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'share'
        
    def __str__(self):
        return f"{self.list} shared by {self.created_by}"
    
    def save(self, *args, **kwargs):
        if not self.url_token:                 
            self.url_token = generate_token()  
        super().save(*args, **kwargs)
    
    
    
    
    
  