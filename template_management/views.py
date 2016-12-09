from django.http.response import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView,\
                                 DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from template_management.models import Template


class TemplateList(LoginRequiredMixin, ListView):
    """TemplateList"""
    model = Template
    template_name = 'template_list.html'

    def get_queryset(self):
        return Template.objects.order_by('-created')\
                               .filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TemplateList, self).get_context_data(**kwargs)
        return context


class TemplateDetail(LoginRequiredMixin, DetailView):
    """TemplateDetail"""
    model = Template
    template_name = 'template_detail.html'

    def get_queryset(self):
        return Template.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TemplateDetail, self).get_context_data(**kwargs)
        return context


class TemplateCreate(LoginRequiredMixin, CreateView):
    """TemplateCreate"""
    model = Template
    fields = ['name', 'html_template', 'text_template', 'placeholders']
    template_name = 'template_new.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(TemplateCreate, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super(TemplateCreate, self).form_invalid(form)


class TemplateUpdate(LoginRequiredMixin, UpdateView):
    """TemplateUpdate"""
    model = Template
    fields = ['name', 'html_template', 'text_template']
    template_name = 'template_edit.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(TemplateUpdate, self).form_valid(form)

    def get_queryset(self):
        return Template.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TemplateUpdate, self).get_context_data(**kwargs)
        return context


class TemplateDelete(LoginRequiredMixin, DeleteView):
    """TemplateDelete"""
    model = Template
    success_url = reverse_lazy('template-list')
    success_message = "The template was deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(TemplateDelete, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return Template.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TemplateDelete, self).get_context_data(**kwargs)
        return context


@login_required
def show_template_preview(request, pk):
    """show_template_preview

    :param request:
    :param pk:
    """
    template = Template.objects.get(pk=pk)
    return HttpResponse(template.html_template)
