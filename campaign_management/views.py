from django.views.generic import ListView, DetailView, CreateView, UpdateView,\
                                 DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.http.response import HttpResponse
from django.views import View

from campaign_management.models import Campaign
from subscriber_management.models import List, Subscriber
from template_management.models import Template

import premailer
from bs4 import BeautifulSoup as HTMLParser


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
    fields = ['email_list', 'name', 'email_subject', 'email_reply_to_email',
              'email_from_name', 'email_from_email', 'email_list']
    template_name = 'campaign_header.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CampaignCreate, self).get_context_data(**kwargs)
        # Allow lists with 0 subscribers
        context['lists'] = List.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CampaignCreate, self).form_valid(form)

    def form_invalid(self, form):
        return super(CampaignCreate, self).form_invalid(form)


class CampaignUpdate(LoginRequiredMixin, UpdateView):
    """CampaignUpdate"""
    model = Campaign
    fields = ['email_list', 'name', 'email_subject', 'email_reply_to_email',
              'email_from_name', 'email_from_email', 'email_list']
    template_name = 'campaign_header.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CampaignUpdate, self).get_context_data(**kwargs)
        context['lists'] = List.objects.filter(user=self.request.user)
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
        email_recipients = request.POST.get('email').split(',')
        email_recipients = [email.replace(' ', '')
                            for email in email_recipients]
        for count, recipient in enumerate(email_recipients):
            # Forbid sending to more than 3 recipients
            if count >= 3:
                break
            campaign = Campaign.objects.get(pk=pk)
            send_mail("[TEST] {}".format(campaign.email_subject),
                      "",
                      campaign.email_from_email,
                      [recipient],
                      fail_silently=False,
                      html_message=campaign.html_template)
    except Exception as ex:
        messages.error(request,
                       "Test email not sent: {}".format(ex),
                       extra_tags='danger')
    else:
        messages.success(request,
                         "Test email successfully sent to {}"
                         .format(", ".join(email_recipients)))
    finally:
        if request.POST.get('redirect-to') == 'compose':
            return redirect('campaign-compose-email', pk=pk)
        else:
            return redirect('campaign-review', pk=pk)


@login_required
def show_campaign_email_preview(request, pk):
    """show_template_preview

    :param request:
    :param pk:
    """
    campaign = Campaign.objects.get(pk=pk)
    if request.GET.get('format') == 'text':
        resp = HttpResponse(campaign.text_template)
        resp['Content-Type'] = 'text/plain; charset=UTF-8'
        return resp
    else:
        return HttpResponse(campaign.html_template)


def _gen_campaign_emails(campaign):
    """_make_newsletter_emails

    :param campaign:
    """
    if not campaign:
        return tuple()
    # If we got a campaign
    subscribers = Subscriber.objects.filter(list=campaign.email_list,
                                            validated=True)
    for subscriber in subscribers:
        _from = "{} <{}>".format(campaign.email_from_name,
                                 campaign.email_from_email)
        email = EmailMultiAlternatives(campaign.email_subject,  # email subject
                                       "",  # body text version
                                       _from,  # from sender
                                       [subscriber.email],  # recipient
                                       reply_to=[campaign.email_reply_to_email])
        email.attach_alternative(campaign.html_template, "text/html")
        # Avoid keepting a list of Object in RAM
        yield email


@login_required
def send_one_campaign_to_one_list(request, pk):
    """send_one_newsletter_to_one_list

    :param request:
    :param pk:
    """

    try:
        campaign = Campaign.objects.get(pk=pk)
        # Start the SMTP connection
        smtp_connection = get_connection()
        smtp_connection.open()
        # Send all emails
        for email in _gen_campaign_emails(campaign):
            email.send()
        # Close connection
        smtp_connection.close()
    except Exception as ex:
        messages.error(request,
                       "Emails not sent: {}".format(ex),
                       extra_tags='danger')
    else:
        messages.success(request,
                         "Emails successfully sent to the list {}"
                         .format(campaign.email_list.name))
        # Update campaign status
        campaign.is_sent = True
        campaign.is_draft = False
        campaign.recipient_count = campaign.email_list.count_validated_subscribers()
        campaign.save()
    finally:
        return redirect('campaign-detail', pk=pk)


class ComposeEmailView(View):

    def get(self, request, pk):
        campaign = Campaign.objects.get(pk=pk)
        return render(request, 'campaign_compose.html', locals())

    def post(self, request, pk):
        html_email = request.POST.get('html_email')
        html_tree = HTMLParser(html_email, "html5lib")
        # Inline CSS from HTML
        # Using regularized/sanitized version by BeautifulSoup
        html_email = premailer.transform(html_tree.prettify(formatter="html"))
        # Use striped tag version of HTML for text
        html_email_body = html_tree.find('body')
        for link in html_email_body.findAll('a'):
            link.replace_with("{} ({})".format(link.text, link.get('href', '')))
        # TODO: Remove the too many white-spaces
        text_email = html_email_body.get_text()
        # Save email HTML and text body
        campaign = Campaign.objects.get(pk=pk)
        campaign.html_template = html_email
        campaign.text_template = text_email
        campaign.save()
        return redirect('campaign-review', pk=pk)
