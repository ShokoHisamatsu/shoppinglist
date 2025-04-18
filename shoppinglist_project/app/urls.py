from django.urls import path
from .views import (
    RegistUserView, HomeView, UserLoginView,
    UserLogoutView, MyListView, HomeView, StoreDeleteView,
    CategoryListView, CategoryItemListView, ItemCategoryCreateView
)


app_name = 'app'
urlpatterns = [
    path('', UserLoginView.as_view(), name='start'),  
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('mylist/<int:store_id>/', MyListView.as_view(), name='mylist'),
    path('store/<int:pk>/delete/', StoreDeleteView.as_view(), name='store_delete'),
    path('store/<int:store_id>/category/', CategoryListView.as_view(), name='category_list'),
    path('store/<int:store_id>/category/<int:category_id>/items/', CategoryItemListView.as_view(), name='category_item_list'),
    path('store/<int:store_id>/category/add/', ItemCategoryCreateView.as_view(), name='itemcategory_add'),
    ]
