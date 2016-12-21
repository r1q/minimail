from django.conf.urls import url, include
from analytics_management import views

urlpatterns = [

    url(r'^$',
        views.HomeView.as_view(),
        name='analytics-management-home'),

    url(r'^list/(?P<uuid>[^/]+)$',
        views.ListView.as_view(),
        name='analytics-management-list'),

    url(r'^list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)$',
        views.CampaignView.as_view(),
        name='analytics-management-campaign'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-stats$',
        views.ApiOpenRateView.as_view(),
        name='analytics-management-api-open-stats'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-date-stats$',
        views.ApiOpenDateView.as_view(),
        name='analytics-management-api-open-date-stats'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-country-stats$',
        views.ApiOpenCountryView.as_view(),
        name='analytics-management-api-open-country-stats'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/click-stats$',
        views.ApiClickRateView.as_view(),
        name='analytics-management-api-click-stats'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/ses-delivery-stats$',
        views.ApiSesDeliveryStatsView.as_view(),
        name='analytics-management-api-ses-delivery-stats'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/ses-complaint-stats$',
        views.ApiSesComplaintStatsView.as_view(),
        name='analytics-management-api-ses-complaint-stats'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/ses-bounce-stats$',
        views.ApiSesBounceStatsView.as_view(),
        name='analytics-management-api-ses-bounce-stats'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/ses-bounce-soft$',
        views.ApiSesBounceSoftView.as_view(),
        name='analytics-management-api-ses-bounce-soft'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/all/ses-suppress-subscribers$',
        views.ApiSesSuppressSubscribersView.as_view(),
        name='analytics-management-api-ses-suppress-subscribers'),

    url(r'^api/list/(?P<list_uuid>[^/]+)/campaign/(?P<campaign_uuid>[^/]+)/open-date/(?P<merger>[^/]+)$',
        views.CampaignApiDateView.as_view(),
        name='analytics-management-api-open-date-by-merger'),

]
