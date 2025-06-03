from django.urls import path, reverse_lazy
from .views import (
    RegistUserView, HomeView, UserLoginView,
    MyListView, StoreDeleteView,
    CategoryListView, CategoryItemListView, ItemCategoryCreateView,
    CategoryAddView, ItemCheckView, ItemDeleteView, EmailChangeView,
    PortfolioView, ItemCategoryDeleteView, CustomLogoutView
)
from . import views
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView, LogoutView, 
)
from django.views.generic import TemplateView


app_name = 'app'
urlpatterns = [
    path('', UserLoginView.as_view(), name='start'),  
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', CustomLogoutView.as_view(next_page='login'), name='user_logout'),
    path('mylist/<int:store_id>/', MyListView.as_view(), name='mylist'),
    path('store/<int:store_id>/delete/', StoreDeleteView.as_view(), name='store_delete'),
    path('store/<int:store_id>/category/', CategoryListView.as_view(), name='category_list'),
    path('store/<int:store_id>/category/<int:category_id>/items/', CategoryItemListView.as_view(), name='category_item_list'),
    path('store/<int:store_id>/category/add/', ItemCategoryCreateView.as_view(), name='itemcategory_add'),
    path('store/<int:store_id>/category/<int:pk>/delete/', ItemCategoryDeleteView.as_view(), name='category_delete'),
    path('mylist/<int:store_id>/category/add/', CategoryAddView.as_view(), name='category_add'),
    path('category_delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('item/<int:item_id>/check/', ItemCheckView.as_view(), name='item_check'),
    path('item/<int:pk>/delete/', ItemDeleteView.as_view(), name='item_delete'),
    path('email_change/', EmailChangeView.as_view(), name='email_change'),
    path('email_change/done/', TemplateView.as_view(template_name='email_change_done.html'), name='email_change_done'),
    path('share/create/<int:store_id>/', views.SharedListCreateView.as_view(), name='shared_list_create'),
    path('share/manage/', views.SharedListManageView.as_view(), name='shared_list_manage'),
    path('share/<slug:url_token>/', views.SharedListDetailView.as_view(), name='shared_list_detail'),
    path('shared/add/', views.SharedListAddView.as_view(), name='shared_list_add'),
    path('share/remove/<slug:url_token>/', views.SharedListRemoveView.as_view(), name='shared_list_remove'),
    ]

urlpatterns +=[
    path('password_change/', PasswordChangeView.as_view(template_name='password_change.html', success_url=reverse_lazy('app:password_change_done')), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(template_name='auth/password_reset_form.html', email_template_name="auth/password_reset_email.txt", subject_template_name="auth/password_reset_subject.txt", success_url=reverse_lazy('app:password_reset_done')), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'), 
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html', success_url=reverse_lazy('app:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
]
