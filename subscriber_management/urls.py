from django.conf.urls import url, include
from subscriber_management import views

urlpatterns = [
    url(r'^$',views.SubscriberListView.as_view(), name='subscriber-management-list'),
    url(r'^list$',views.SubscriberListView.as_view(), name='subscriber-management-list'),
    url(r'^list/(?P<uuid>[^/]+)/$',views.SubscriberListSubscribersView.as_view(), name='subscriber-management-list-subscribers'),
    url(r'^list/(?P<uuid>[^/]+)/delete$',views.SubscriberListDeleteView.as_view(), name='subscriber-management-list-delete'),
    url(r'^list/(?P<uuid>[^/]+)/join$',views.SubscribeJoin.as_view(), name='subscriber-management-join'),
    url(r'^create$',views.SubscriberCreateView.as_view(), name='subscriber-management-create'),
]
