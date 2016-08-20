from django.conf.urls import url
from django.contrib import admin
from template_management import views


urlpatterns = [
    # Template actions
    url(r'^new', views.create_template),
    url(r'^(?P<template_id>\d+)/edit', views.edit_template),
    url(r'^(?P<template_id>\d+)/preview', views.show_template_preview),
    url(r'^(?P<template_id>\d+)/delete', views.delete_template),
    url(r'^(?P<pk>\d+)', views.TemplateDetail.as_view()),
    # Template listing actions
    url(r'^', views.TemplateList.as_view()),
]
