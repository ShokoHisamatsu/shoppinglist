from django.urls import path
from . import views 


app_name = "app"
urlpatterns = [
    path("register_view", views.register_view, name="register_view"),
    ]