from django.conf.urls import url, include
from user_management import views

urlpatterns = [
    url(r'^account/register$',views.Register.as_view(), name='user_register'),
    url(r'^account/login$',views.Login.as_view(), name='user_login'),
    url(r'^account$',views.UserUpdateView.as_view(), name='user_account'),
]
