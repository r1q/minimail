from django.views.generic import ListView, DetailView, CreateView, UpdateView,\
                                 DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from campaign_management.models import Campaign
from subscriber_management.models import List
from template_management.models import Template


class CampaignList(LoginRequiredMixin, ListView):
    """CampaignList"""
    model = Campaign
    template_name = 'campaign_list.html'

    def get_queryset(self):
        return Campaign.objects.select_related('email_list').order_by('-created')\
                               .filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CampaignList, self).get_context_data(**kwargs)
        return context


class CampaignDetail(LoginRequiredMixin, DetailView):
    """CampaignDetail"""
    model = Campaign
    template_name = 'campaign_detail.html'

    def get_queryset(self):
        return Campaign.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CampaignDetail, self).get_context_data(**kwargs)
        return context


class CampaignCreate(LoginRequiredMixin, CreateView):
    """CampaignCreate"""
    model = Campaign
    fields = ['email_list', 'email_template', 'name', 'email_subject',
              'email_from_name', 'email_from_email', 'email_list', 'email_template']
    template_name = 'campaign_new.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CampaignCreate, self).get_context_data(**kwargs)
        context['lists'] = List.objects.filter(user=self.request.user)
        context['templates'] = Template.objects.filter(author=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CampaignCreate, self).form_valid(form)

    def form_invalid(self, form):
        return super(CampaignCreate, self).form_invalid(form)


class CampaignUpdate(LoginRequiredMixin, UpdateView):
    """CampaignUpdate"""
    model = Campaign
    fields = ['name', 'html_campaign', 'text_campaign']
    template_name = 'campaign_edit.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CampaignUpdate, self).form_valid(form)

    def get_queryset(self):
        return Campaign.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CampaignUpdate, self).get_context_data(**kwargs)
        return context


class CampaignDelete(LoginRequiredMixin, DeleteView):
    """CampaignDelete"""
    model = Campaign
    success_url = reverse_lazy('campaign-list')
    success_message = "The campaign was deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(CampaignDelete, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return Campaign.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CampaignDelete, self).get_context_data(**kwargs)
        return context
