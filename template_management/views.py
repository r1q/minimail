from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.generic import ListView, DetailView

from template_management.models import Template


class TemplateList(ListView):
  model = Template
  queryset = Template.objects.order_by('-created')
  template_name = 'template_list.html'


class TemplateDetail(DetailView):
  model = Template
  template_name = 'template_detail.html'


def create_template(request, template_id):
  pass


def show_template(request, template_id):
  pass


def edit_template(request, template_id):
  pass


def show_template_preview(request, template_id):
  template = Template.objects.get(id=template_id)
  return HttpResponse(template.html_template)


def delete_template(request, template_id):
  pass
