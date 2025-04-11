from django.urls import path
from .views import (
    RegistUserView, HomeView, UserLoginView,
    UserLogoutView, MyListView,
)


app_name = 'app'
urlpatterns = [
    path('', UserLoginView.as_view(), name='start'),  
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('mylist/', MyListView.as_view(), name='mylist'),
    ]
