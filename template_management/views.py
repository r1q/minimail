from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from template_management.models import Template


class TemplateList(ListView):
  model = Template
  queryset = Template.objects.order_by('-created')
  template_name = 'template_list.html'


class TemplateDetail(DetailView):
  model = Template
  template_name = 'template_detail.html'


class TemplateCreate(CreateView):
  model = Template
  fields = ['name', 'html_template']
  template_name = 'template_new.html'

  def form_valid(self, form):
    form.instance.author = self.request.user
    return super(TemplateCreate, self).form_valid(form)

  def form_invalid(self, form):
    return super(TemplateCreate, self).form_valid(form)


class TemplateUpdate(UpdateView):
  model = Template
  fields = ['name', 'html_template']
  template_name = 'template_new.html'

  @login_required
  def form_valid(self, form):
    form.instance.author = self.request.user
    return super(TemplateCreate, self).form_valid(form)


class TemplateDelete(DeleteView):
  model = Template
  success_url = reverse_lazy('template-list')


def show_template_preview(request, pk):
  template = Template.objects.get(pk=pk)
  return HttpResponse(template.html_template)
