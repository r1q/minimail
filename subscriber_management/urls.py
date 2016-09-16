from django.conf.urls import url, include
from subscriber_management import views

urlpatterns = [
    url(r'^$',views.SubscriberListView.as_view(), name='subscriber-management-list'),
    url(r'^list$',views.SubscriberListView.as_view(), name='subscriber-management-list'),
    url(r'^list/(?P<uuid>[^/]+)/$',views.SubscriberListSubscribersView.as_view(), name='subscriber-management-list-subscribers'),
    url(r'^list/(?P<uuid>[^/]+)/signup$',views.SubscriberListSignUpForm.as_view(), name='subscriber-management-list-sign-up-form'),
    url(r'^list/(?P<uuid>[^/]+)/bulk$',views.SubscriberListSubscribersBulkView.as_view(), name='subscriber-management-list-subscribers-bulk'),
    url(r'^list/(?P<uuid>[^/]+)/delete$',views.SubscriberListDeleteView.as_view(), name='subscriber-management-list-delete'),
    url(r'^list/(?P<uuid>[^/]+)/settings',views.SubscriberListSettingsView.as_view(), name='subscriber-management-list-settings'),
    url(r'^list/(?P<uuid>[^/]+)/nl-homepage',views.SubscriberListNewsletterHomepageView.as_view(), name='subscriber-management-list-newsletter-homepage'),
    url(r'^list/(?P<uuid>[^/]+)/join$',views.SubscriberJoin.as_view(), name='subscriber-management-join'),
    url(r'^list/(?P<uuid>[^/]+)/join-success$',views.SubscriberJoinSuccess.as_view(), name='subscriber-management-join-success'),
    url(r'^list/(?P<uuid>[^/]+)/join-error$',views.SubscriberJoinError.as_view(), name='subscriber-management-join-error'),
    url(r'^list/(?P<uuid>[^/]+)/import$',views.SubscriberListImportCSV.as_view(), name='subscriber-management-list-import'),
    url(r'^list/(?P<uuid>[^/]+)/subscriber/(?P<subscriber_uuid>[^/]+)/delete',views.SubscriberDeleteView.as_view(), name='subscriber-management-subscriber-delete'),
    url(r'^create$',views.SubscriberListCreateView.as_view(), name='subscriber-management-create'),
    url(r'^subscriber/(?P<uuid>[^/]+)/unsubscribe/(?P<token>[^/]+)$',views.SubscriberUnsubscribeView.as_view(), name='subscriber-management-subscriber-unsubscribe'),

]
