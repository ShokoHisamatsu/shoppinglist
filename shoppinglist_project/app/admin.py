from django.contrib import admin
from .models import User, ShoppingList, ShoppingItem, Store, ItemCategory, List_ItemCategory, SharedList

admin.site.register(User)
admin.site.register(Store)
admin.site.register(ShoppingList)
admin.site.register(ItemCategory)
admin.site.register(ShoppingItem)
admin.site.register(List_ItemCategory)
admin.site.register(SharedList)

# Register your models here.
