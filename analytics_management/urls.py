from django.conf.urls import url, include
from analytics_management import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='analytics-management-home'),
    url(r'^list/(?P<uuid>[^/]+)$', views.ListView.as_view(), name='analytics-management-list'),
    url(r'^list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)$', views.CampaignView.as_view(), name='analytics-management-campaign'),
    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-rate$', views.ApiOpenRateView.as_view(), name='analytics-management-api-open-rate'),
    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-date$', views.ApiOpenDateView.as_view(), name='analytics-management-api-open-date'),
    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-country$', views.ApiOpenCountryView.as_view(), name='analytics-management-api-open-country'),
    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-date/(?P<merger>[^/]+)$', views.CampaignApiDateView.as_view(), name='analytics-management-api-open-date-by-merger'),
    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/click-rate$', views.ApiClickRateView.as_view(), name='analytics-management-api-click-rate'),
    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/ses-rate$', views.ApiSesRateView.as_view(), name='analytics-management-api-ses-rate'),
]
