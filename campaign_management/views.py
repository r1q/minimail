from django.views.generic import ListView, DetailView, CreateView, UpdateView,\
                                 DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.mail import send_mail

from campaign_management.models import Campaign
from subscriber_management.models import List
from template_management.models import Template


class CampaignList(LoginRequiredMixin, ListView):
    """CampaignList"""
    model = Campaign
    template_name = 'campaign_list.html'

    def get_queryset(self):
        return Campaign.objects.select_related('email_list')\
                               .order_by('-created')\
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


class CampaignReview(LoginRequiredMixin, DetailView):
    """CampaignDetail"""
    model = Campaign
    template_name = 'campaign_review.html'

    def get_queryset(self):
        return Campaign.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CampaignReview, self).get_context_data(**kwargs)
        return context


class CampaignCreate(LoginRequiredMixin, CreateView):
    """CampaignCreate"""
    model = Campaign
    fields = ['email_list', 'email_template', 'name', 'email_subject',
              'email_from_name', 'email_from_email', 'email_list',
              'email_template']
    template_name = 'campaign_new_or_edit.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CampaignCreate, self).get_context_data(**kwargs)
        context['lists'] = List.objects.filter(user=self.request.user)
        context['templates'] = Template.objects\
                                       .filter(author=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CampaignCreate, self).form_valid(form)

    def form_invalid(self, form):
        return super(CampaignCreate, self).form_invalid(form)


class CampaignUpdate(LoginRequiredMixin, UpdateView):
    """CampaignUpdate"""
    model = Campaign
    fields = ['email_list', 'email_template', 'name', 'email_subject',
              'email_from_name', 'email_from_email', 'email_list',
              'email_template']
    template_name = 'campaign_new_or_edit.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CampaignUpdate, self).get_context_data(**kwargs)
        context['lists'] = List.objects.filter(user=self.request.user)
        context['templates'] = Template.objects\
                                       .filter(author=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CampaignUpdate, self).form_valid(form)

    def get_queryset(self):
        return Campaign.objects.filter(author=self.request.user)


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


@login_required
def send_test_email(request, pk):
    """send_test_email

    :param req:
    :param campaign_id:
    """

    try:
        email_recipient = request.POST.get('email')
        campaign = Campaign.objects.select_related('email_template').get(pk=pk)
        send_mail("[TEST] {}".format(campaign.email_subject),
                  "",
                  campaign.email_from_email,
                  [email_recipient],
                  fail_silently=False,
                  html_message=campaign.email_template.html_template)
    except Exception as ex:
        messages.error(request,
                       "Test email not sent: {}".format(ex),
                       extra_tags='danger')
    else:
        messages.success(request,
                         "Test email successfully sent to {}"
                         .format(email_recipient))
    finally:
        return redirect('campaign-review', pk=pk)
