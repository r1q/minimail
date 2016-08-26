from django.conf.urls import url
from template_management import views


urlpatterns = [

    url(r'^new',
        views.TemplateCreate.as_view(),
        name='template-new'),

    url(r'^(?P<pk>\d+)/edit',

        views.TemplateUpdate.as_view(),
        name='template-update'),

    url(r'^(?P<pk>\d+)/delete',
        views.TemplateDelete.as_view(),
        name='template-delete'),

    url(r'^(?P<pk>\d+)/preview',
        views.show_template_preview,
        name='template-preview'),

    url(r'^(?P<pk>\d+)',
        views.TemplateDetail.as_view(),
        name='template-detail'),

    url(r'^',
        views.TemplateList.as_view(),
        name='template-list'),

]
