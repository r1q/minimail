from django.conf.urls import url, include
from analytics_management import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='analytics-management-home'),
    url(r'^list/(?P<uuid>[^/]+)$', views.ListView.as_view(), name='analytics-management-list'),
    url(r'^list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)$', views.CampaignView.as_view(), name='analytics-management-campaign'),
]
