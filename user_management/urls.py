from django.conf.urls import url, include
from user_management import views

urlpatterns = [
    url(r'^account$',views.UserUpdateView.as_view(), name='user_account'),
]
