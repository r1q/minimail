from django.conf.urls import url
from campaign_management import views


urlpatterns = [

    url(r'^new',
        views.CampaignCreate.as_view(),
        name='campaign-new'),

    url(r'^(?P<pk>\d+)/email-preview',
        views.show_campaign_email_preview,
        name='campaign-email-preview'),

    url(r'^(?P<pk>\d+)/review',
        views.CampaignReview.as_view(),
        name='campaign-review'),

    url(r'^(?P<pk>\d+)/edit',
        views.CampaignUpdate.as_view(),
        name='campaign-update'),

    url(r'^(?P<pk>\d+)/delete',
        views.CampaignDelete.as_view(),
        name='campaign-delete'),

    url(r'^(?P<pk>\d+)/send-campaign',
        views.send_one_campaign_to_one_list,
        name='campaign-send-campaign'),

    url(r'^(?P<pk>\d+)/send-test-email',
        views.send_test_email,
        name='campaign-send-test-email'),

    url(r'^(?P<pk>\d+)',
        views.CampaignDetail.as_view(),
        name='campaign-detail'),

    url(r'^',
        views.CampaignList.as_view(),
        name='campaign-list'),

]
