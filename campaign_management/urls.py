from django.conf.urls import url
from campaign_management import views


urlpatterns = [

    url(r'^new',
        views.CampaignCreate.as_view(),
        name='campaign-new'),

    url(r'^(?P<pk>\d+)/edit',
        views.CampaignUpdate.as_view(),
        name='campaign-update'),

    url(r'^(?P<pk>\d+)/delete',
        views.CampaignDelete.as_view(),
        name='campaign-delete'),

    url(r'^(?P<pk>\d+)',
        views.CampaignDetail.as_view(),
        name='campaign-detail'),

    url(r'^',
        views.CampaignList.as_view(),
        name='campaign-list'),

]
