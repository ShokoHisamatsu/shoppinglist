from django.contrib import admin
from .models import User, ShoppingList, ShoppingItem, Store, ItemCategory, List_ItemCategory, SharedList

admin.site.register(User)
admin.site.register(Store)
admin.site.register(ShoppingList)
admin.site.register(ItemCategory)
admin.site.register(SharedList)

# Register your models here.

@admin.register(List_ItemCategory)
class ListItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('list', 'get_created_by', 'item_category')

    def get_created_by(self, obj):
        return obj.list.created_by  # または obj.list.user
    get_created_by.short_description = '作成者'
    
    
@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ('shopping_list', 'get_created_by', 'commodity', 'quantity', 'memo')

    def get_created_by(self, obj):
        return obj.shopping_list.created_by
    get_created_by.short_description = '作成者'
