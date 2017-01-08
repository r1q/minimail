from django.conf.urls import url, include
from user_management import views

urlpatterns = [
    # Homepage
    url(r'^$', views.homepage, name='homepage'),

    url(r'^account/register$',views.Register.as_view(), name='user_register'),
    url(r'^account/login$',views.Login.as_view(), name='user_login'),
    url(r'^account/change_password$',views.UpdatePasswordView.as_view(), name='user_change_password'),
    url(r'^account/logout$',views.logout_view, name='user_logout'),
    url(r'^account/forgotten$',views.Forgotten.as_view(), name='user_forgotten'),
    url(r'^account/recovery/(?P<uuid>[^/]+)$',views.Recovery.as_view(), name='user_recovery'),
    url(r'^account$',views.UserUpdateView.as_view(), name='user_account'),
]
