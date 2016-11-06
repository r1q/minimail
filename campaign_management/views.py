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

from premailer import Premailer
from bs4 import BeautifulSoup as HTMLParser
from bs4.dammit import EntitySubstitution
import htmlmin
import multiprocessing as mp
import simplejson as json


def _custom_substitute_html_entities(text):
    """
        Substitute all special characters to their HTML entities,
        with the exception for template tags.
    """
    if text.strip().startswith('*|') and text.strip().endswith('|*'):
        return text
    else:
        return EntitySubstitution.substitute_html(text)


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
    # TODO: If no unsubscribe link, append HTML snippet with it

    def get_queryset(self):
        return Campaign.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CampaignReview, self).get_context_data(**kwargs)
        context['is_from_email_verified'] = List.objects.filter(user=self.request.user,
                                                                from_email_verified=True)\
                                                        .exists()
        return context


class CampaignCreate(LoginRequiredMixin, CreateView):
    """CampaignCreate"""
    model = Campaign
    fields = ['email_list', 'name', 'email_subject', 'email_reply_to_email',
              'email_from_name', 'email_list']
    template_name = 'campaign_header.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CampaignCreate, self).get_context_data(**kwargs)
        context['from_emails'] = List.objects.filter(user=self.request.user,
                                                     from_email_verified=True)\
                                             .values_list('from_email', flat=True)
        # Allow lists with 0 subscribers
        context['lists'] = List.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        from_email = List.objects.get(pk=form.instance.email_list.id).from_email
        form.instance.email_from_email = from_email
        # if not available in the page.
        return super(CampaignCreate, self).form_valid(form)

    def form_invalid(self, form):
        return super(CampaignCreate, self).form_invalid(form)


class CampaignUpdate(LoginRequiredMixin, UpdateView):
    """CampaignUpdate"""
    model = Campaign
    fields = ['email_list', 'name', 'email_subject', 'email_reply_to_email',
              'email_from_name', 'email_list']
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
                      campaign.email_list.from_email,
                      [recipient],
                      fail_silently=False,
                      html_message=campaign.html_email_for_sending)
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
        resp = HttpResponse(campaign.text_email)
        resp['Content-Type'] = 'text/plain; charset=UTF-8'
        return resp
    else:
        return HttpResponse(campaign.html_email_for_sending)


def _inject_unsubscribe_link(subscriber, campaign):
    unsubscribe_link = subscriber.unsubscribe_link()
    html_email = campaign.html_email_for_sending.replace('*%7CUNSUB%7C*',
                                             unsubscribe_link)
    text_email = campaign.text_email.replace('*%7CUNSUB%7C*',
                                             unsubscribe_link)
    html_email = campaign.html_email_for_sending.replace('*|UNSUB|*',
                                             unsubscribe_link)
    text_email = campaign.text_email.replace('*|UNSUB|*',
                                             unsubscribe_link)
    return html_email, text_email


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
        # TODO: Remember at what byte offset we inject the  unsubscribe_link,
        #       to prefer string O(n) search each time
        html_email, text_email = _inject_unsubscribe_link(subscriber, campaign)
        # TODO: Inject tracking pixel
        _from = "{} <{}>".format(campaign.email_from_name,
                                 campaign.email_list.from_email)
        email = EmailMultiAlternatives(campaign.email_subject,  # email subject
                                       text_email,  # body text version
                                       _from,  # from sender
                                       [subscriber.email],  # recipient
                                       reply_to=[campaign.email_reply_to_email])
        email.attach_alternative(html_email, "text/html")
        # Avoid keepting a list of Object in RAM
        yield email


@login_required
def send_one_campaign_to_one_list(request, pk):
    """send_one_newsletter_to_one_list

    :param request:
    :param pk:
    """

    try:
        campaign = Campaign.objects.select_related('email_list').get(pk=pk)
        # Start the SMTP connection
        smtp_connection = get_connection()
        smtp_connection.open()
        # Send all emails
        # TODO: Should be done concurrently
        for email in _gen_campaign_emails(campaign):
            if not email:
                # TODO: Log fail to generate email
                continue
            else:
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


def _textify_html_email(html_email_body_root):
    try:
        # Reformat links
        for link in html_email_body_root.findAll('a'):
            link.replace_with("{} ({})".format(link.text, link.get('href', '')))
        # Reformat headers
        for h1 in html_email_body_root.findAll('h1'):
            h1.text.replace("# {}".format(h1.text), h1.text)
        for h2 in html_email_body_root.findAll('h2'):
            h2.text.replace("## {}".format(h2.text), h2.text)
        for h3 in html_email_body_root.findAll('h3'):
            h3.text.replace("### {}".format(h3.text), h3.text)
        # TODO: Remove the too many white-spaces
        # Get striped tags version
        text_email = html_email_body_root.get_text()
    except Exception as ex:
        print(ex)
        text_email = ""
    finally:
        return text_email


class ComposeChooseTemplateView(View):

    def get(self, request, pk):
        campaign = Campaign.objects.get(pk=pk)
        # Redirect to compose screen of template already picked
        if campaign.using_template:
            return redirect('campaign-compose-email', pk=pk)
        else:
            all_templates = Template.objects.filter(author=self.request.user)
            return render(request, 'campaign_choose_template.html', locals())

    def post(self, request, pk):
        campaign = Campaign.objects.get(pk=pk)
        template_id = request.POST.get('template_id')
        template = Template.objects.get(id=template_id)
        campaign.using_template = template
        campaign.save()
        return redirect('campaign-compose-email', pk=pk)


class ComposeEmailView(View):

    def get(self, request, pk):
        campaign = Campaign.objects.select_related('using_template').get(pk=pk)
        template = campaign.using_template
        if not template:
            return redirect('campaign-choose-tmplt', pk=pk)
        else:
            for t_k, t_v in template.placeholders.items():
                if campaign.placeholders_value and t_k in campaign.placeholders_value:
                    new_attrs = {'value': campaign.placeholders_value.get(t_k, '')}
                    template.placeholders[t_k].update(new_attrs)
            campaign.placeholders_value = json.dumps(campaign.placeholders_value)
            return render(request, 'campaign_compose.html', locals())

    def post(self, request, pk):
        # Save edited HTML and placeholders value
        html_email = request.POST.get('html_email', '')
        placeholders_value = request.POST.get('placeholders_value', '')
        campaign = Campaign.objects.get(pk=pk)
        # Only save if we have something
        has_changed = False
        if len(placeholders_value.strip()) > 1:
            campaign.placeholders_value = json.loads(placeholders_value)
            has_changed = True
        if len(html_email.strip()) > 1:
            campaign.html_email_for_editing = html_email
            campaign.html_email_for_sending = html_email
            has_changed = True
        if has_changed:
            campaign.save()
        # Regularize/Sanitize HTML with BeautifulSoup
        html_tree = HTMLParser(html_email, "html5lib")
        # TODO: Delete any <script> tag
        # normalized_html = html_tree.prettify(formatter=_custom_substitute_html_entities)
        # Inline CSS from HTML
        # css_inliner = Premailer(normalized_html,
        #                        keep_style_tags=True,
        #                        preserve_internal_links=True,
        #                        include_star_selectors=True)
        #inlined_html_email = css_inliner.transform()
        # Minify HTML (gmail cut long emails, char limit)
        #minified_html_email = htmlmin.minify(inlined_html_email)
        # Use striped tag version of HTML for text
        text_email = _textify_html_email(html_tree.find('body'))
        # Save email HTML and text body
        campaign.html_email_for_sending = html_email
        campaign.text_email = text_email
        campaign.is_composed = True
        campaign.save()
        return redirect('campaign-review', pk=pk)
