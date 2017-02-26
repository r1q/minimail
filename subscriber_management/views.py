"""
view.py contains all the logic for subscriber lists and associated
subscribers.
"""

import django.db.utils
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.views import View
from django.http import Http404
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.models import Sum

import csv
from datetime import datetime
import json
from contextlib import closing
from io import StringIO
import pandas
from localize import geo, timezone
import uuid
import traceback

from subscriber_management.models import List, Subscriber
from subscriber_management.forms import ListForm, SubscriberForm, \
    ListSettingsForm, ListNewsletterHomepage, ListNewsletterImportCSV
from campaign_management.models import Campaign
from analytics_management.models import OpenRate, ClickRate


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

VALIDATION_EMAIL = _("""
{}

Click this link to confirm your subscription:
{}

If you didn't subscribe, you can ignore this email. You won't be subscribed if you don't click the link above.


— Sent with Minimail
""")


def _send_validation_email(list_name, subscriber):
    send_mail(
        "{}: {}".format(list_name, _('Please Confirm Subscription')), # Subject
        VALIDATION_EMAIL.format(list_name, subscriber.validation_link()), # Text email
        '{} <{}>'.format(list_name, 'hi@fullweb.io'), # From: email
        [subscriber.email], # To:
        fail_silently=False,
    )


class SubscriberListView(LoginRequiredMixin, ListView):

    """
    SubscriberListView display subscribers lists that belongs to a user.
    """

    model = List
    template_name = 'list_list.html'
    context_object_name = 'subscriber_lists'

    def get_queryset(self):
        return List.objects.filter(user__id=self.request.user.id)\
                           .order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(SubscriberListView, self).get_context_data(**kwargs)
        for email_list in self.object_list:
            try:
                c = Campaign.objects.filter(author=self.request.user,
                                            email_list=email_list)\
                                    .order_by('-edited')
                email_list.draft_count = c.filter(is_sent=False, is_draft=True).count()
                email_list.sent_count = c.filter(is_sent=True, is_draft=False).count()
                email_list.last_email_sent = c[0].sent
                email_list.open_rate = OpenRate.objects.filter(list=c.email_list)\
                                                       .aggregate(Sum('unique_count'))
                email_list.click_rate = ClickRate.objects.filter(list=c.email_list)\
                                                         .aggregate(Sum('unique_count'))
            except Exception as e:
                print(e)
                continue
        return context


class SubscriberListCreateView(LoginRequiredMixin, CreateView):

    """
    SubscriberCreateView create a new empty list of subscribers.
    """

    model = List
    template_name = 'list_create.html'
    form_class = ListForm
    success_message = _(" was successfully created")

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Record the user has at least 1 list
        if not self.request.user.has_a_list:
            self.request.user.has_a_list = True
            self.request.user.save()
        messages.success(self.request, form.instance.name + self.success_message)
        return super(SubscriberListCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SubscriberListCreateView, self).form_invalid(form)

    def get_success_url(self):
        return self.request.POST.get('success_url', '/subscribers')


class SubscriberListSettingsView(LoginRequiredMixin, View):

    """
    SubscriberListSettingsView updates an existing list for subscribers.
    """

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid, user=self.request.user)
        form_object = ListSettingsForm(instance=list_item)
        return render(request, "list_settings.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid, user=self.request.user)
        form_object = ListSettingsForm(request.POST, instance=list_item)
        if form_object.is_valid():
            messages.success(self.request,
                             _("List settings successfully updated"))
            form_object.save()
            return redirect('subscriber-management-list-settings', uuid)
        else:
            return render(request, "list_settings.html", locals())


class SubscriberListNewsletterHomepageView(LoginRequiredMixin, View):

    """
    SubscriberListNewsletterHomepageView updates an existing list for subscribers.
    """

    success_message = _(" was successfully updated")

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        form_object = ListNewsletterHomepage(instance=list_item)
        return render(request, "list_newsletter_homepage.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        form_object = ListNewsletterHomepage(request.POST, request.FILES, instance=list_item)
        if form_object.is_valid():
            form_object.save()
            messages.success(self.request, form_object.instance.name + self.success_message)
            return redirect('subscriber-management-list-newsletter-homepage', uuid)
        return render(request, "list_newsletter_homepage.html", locals())


class SubscriberListSignUpForm(LoginRequiredMixin, View):

    """
    SubscriberListSignUpForm displays the signup form
    """

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        return render(request, "subscriber_signup_form.html", locals())


class SubscriberListDeleteView(LoginRequiredMixin, View):

    """
    SubscriberListDeleteView deletes a subscriber list and all it
    associated subscribers.
    """

    success_message = " was successfully deleted"

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        Subscriber.objects.filter(list__id=list_item.id).delete()
        list_item.delete()
        # Record the user has no list anymore, if that's the case
        if self.request.user.has_a_list:
            if not List.objects.filter(user=self.request.user).exists():
                self.request.user.has_a_list = False
                self.request.user.save()
        messages.success(request, list_item.name + self.success_message)
        return redirect('subscriber-management-list')


class SubscriberListImportCSV(LoginRequiredMixin, View):

    """
    SubscriberListImportCSV import and parse a csv file from mailchimp.
    Subscribers are automatically considered as 'validated'.
    """

    SUCCESS_MESSAGE = _(" subscribers imported")

    def post(self, request, list_uuid):
        try:
            form = ListNewsletterImportCSV(request.POST, request.FILES)
            if form.is_valid():
                # Get the list we work with
                list_item = List.objects.get(uuid=list_uuid)
                # TODO: If list already has subcribers, don't use COPY
                # Get the count before inserting new subscribers
                before_insert_count = list_item.count_all_subscribers()
                # Read uploaded CSV file
                df_emails = pandas.read_csv(request.FILES['csv_file'], usecols=[0], engine='c',
                                            keep_default_na=False, dtype='str', skipinitialspace=True,
                                            error_bad_lines=False, dialect='unix')
                # Clean: remove duplicated and empty rows
                df_emails = df_emails.drop_duplicates('Email Address')
                df_emails = df_emails.dropna(how='all')
                # Remove file from RAM
                del request.FILES['csv_file']
                line_count = df_emails.shape[0]
                # Build dataframe for other attributes
                df_list = pandas.DataFrame([str(list_item.id)]*line_count)
                now = datetime.now()
                df_created = pandas.DataFrame([now]*line_count)
                df_edited = pandas.DataFrame([now]*line_count)
                df_validated = pandas.DataFrame([True]*line_count)
                df_imported = pandas.DataFrame([True]*line_count)
                df_uuid = pandas.DataFrame(['']*line_count).applymap(lambda x: str(uuid.uuid4()))
                df_ts = pandas.DataFrame(['']*line_count).applymap(lambda x: str(uuid.uuid4()))
                df_tu = pandas.DataFrame(['']*line_count).applymap(lambda x: str(uuid.uuid4()))
                # Set sanitized CSV column order
                col_in_order = [df_list, df_uuid, df_created, df_edited, df_ts,
                                df_tu, df_validated, df_imported]
                # Concat it all column-wise
                df_final_csv = pandas.concat(col_in_order, axis=1, ignore_index=True)
                df_final_csv = pandas.concat([df_emails, df_final_csv], axis=1, ignore_index=True, join='inner',
                                             verify_integrity=True)
                # Last clean all rows with empty value check
                df_final_csv.dropna(how='all', inplace=True, axis=0)
                # Output as a CSV into buffer
                s_buf = StringIO()
                df_final_csv.to_csv(s_buf, index=False, header=None)
                s_buf.seek(0)
                # COPY buffer into subscriber_management_subscriber table
                with closing(connection.cursor()) as cursor:
                    cursor.copy_from(
                                    file=s_buf,
                                    table='subscriber_management_subscriber',
                                    sep=',',
                                    columns=('email', 'list_id', 'uuid', 'created', 'edited', 'token_subscribe',
                                             'token_unsubscribe', 'validated', 'imported')
                                )

            else:
                raise Exception('Form not valid: {}'.format(form.errors))
        except Exception as e:
            messages.error(request, str(e), extra_tags="danger")
        else:
            # Get the count after inserting new subscribers
            saved_count = list_item.count_all_subscribers() - before_insert_count
            messages.success(request, str(saved_count) + self.SUCCESS_MESSAGE)
            # Record this user has passed the subscribers import step (asked on
            # very first onboarding)
            request.user.has_passed_subscribers_import_step = True
            request.user.save()
        finally:
            if request.POST.get('success_url'):
                return redirect(request.POST.get('success_url'))
            else:
                return redirect('subscriber-management-list-subscribers', list_uuid)


class SubscriberListImportText(LoginRequiredMixin, View):

    """
    SubscriberListImportText import and parse a text input.
    Subscribers are automatically considered as 'validated'.
    """

    success_message = _(" subscriber(s) imported")

    def save_user(self, list_item, row):
        try:
            new_subscriber = Subscriber()
            new_subscriber.list = list_item
            new_subscriber.email = row[0].strip()
            name_info = row[1].split(' ')
            if len(name_info) >= 2:
                new_subscriber.first_name = name_info[0]
                new_subscriber.last_name = ' '.join(name_info[1:])
            elif len(name_info) == 1:
                new_subscriber.first_name = name_info[0]
            else:
                pass
            new_subscriber.timezone = "GMT"
            new_subscriber.country = timezone.timezone_to_iso_code(new_subscriber.timezone)
            new_subscriber.validated = True
            new_subscriber.save()
        except Exception as e:
            return False
        else:
            return True

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        if 'text_import' not in request.POST:
            return redirect('subscriber-management-list-subscribers', uuid)
        content = request.POST['text_import']
        save_count = 0
        lines_csv = content.split('\n')
        lines_count = min(100, len(lines_csv))
        for row in csv.reader(lines_csv[0:lines_count]):
            if len(row) != 2:
                continue
            if row[0].strip() == '':
                continue
            if self.save_user(list_item, row) == True:
                save_count += 1
        messages.success(request, str(save_count) + self.success_message)
        return redirect('subscriber-management-list-subscribers', uuid)


class SubscriberListSubscribersView(LoginRequiredMixin, ListView):

    """
    SubscriberListSubscribersView list all the subscribers associated to a list.
    """

    model = Subscriber
    template_name = 'subscriber_list.html'
    context_object_name = 'subscribers'

    def get_queryset(self):
        list_uuid = self.kwargs['uuid']
        return Subscriber.objects.filter(list__uuid=list_uuid,validated=True).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(SubscriberListSubscribersView, self).get_context_data(**kwargs)
        list_uuid = self.kwargs['uuid']
        context['list_item'] = List.objects.get(uuid=list_uuid,
                                                user=self.request.user)
        context['total_count'] = context['subscribers'].count()
        context['open_rate'] = OpenRate.objects.filter(list=context['list_item'])\
                                               .aggregate(Sum('unique_count'))
        context['click_rate'] = ClickRate.objects.filter(list=context['list_item'])\
                                                 .aggregate(Sum('unique_count'))
        paginator = Paginator(context['subscribers'], 50)
        page = self.request.GET.get('page')
        try:
            context['subscribers'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['subscribers'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['subscribers'] = paginator.page(paginator.num_pages)
        context['paginator'] = paginator
        context['page_nums'] = range(1, paginator.num_pages+1)

        return context


class SubscriberListSubscribersBulkView(LoginRequiredMixin, View):

    def post(self, request, uuid):
        if 'user_list' not in request.POST:
            return redirect('subscriber-management-list-subscribers', uuid)
        subs = json.loads(request.POST['user_list'])
        for subscriber_uuid in subs:
            try:
                Subscriber.objects.get(list__uuid=uuid, uuid=subscriber_uuid).delete()
            except:
                pass
        return redirect('subscriber-management-list-subscribers', uuid)


class SubscriberJoin(View):

    """
    SubscriberJoin display a form where a new subscriber can join a list.
    The new subscriber will have to validate his email by clicking a
    validation link,
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(SubscriberJoin, self).dispatch(*args, **kwargs)

    def _get_client_ip(self, req):
        if req.META.get('HTTP_X_FORWARDED_FOR'):
            return req.META.get('HTTP_X_FORWARDED_FOR')
        else:
            return req.META.get('REMOTE_ADDR')

    def _get_country_from_ip(self, req):
        ip = self._get_client_ip(req)
        return geo.get_country_code(ip)

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        try:
            last_campaign = Campaign.objects.filter(email_list=list_item).latest('sent')
        except Campaign.DoesNotExist:
            last_campaign = None
        form = SubscriberForm()
        return render(request, "subscriber_join.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        if list_item.signup_token() in request.POST:
            if request.POST[list_item.signup_token()] != "":
                if request.is_ajax():
                    return JsonResponse({"error": 'signup token not empty'})
                else:
                    messages.error(request, _("Error while submitting the form. Please refresh the page and try again."))
                    return redirect('subscriber-management-join', uuid)
        else:
            if request.is_ajax():
                return JsonResponse({"error": "signup token not empty"})
            else:
                messages.error(request, _("Error while submitting the form. Please refresh the page and try again."))
                return redirect('subscriber-management-join', uuid)

        form = SubscriberForm(request.POST)
        try:
            if form.is_valid():
                form.instance.list = list_item
                form.instance.ip = self._get_client_ip(request)
                form.instance.country = self._get_country_from_ip(request)
                form.instance.timezone = geo.get_timezone(form.instance.ip)
                form.instance.user_agent = request.META.get('HTTP_USER_AGENT', '')
                form.instance.accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
                try:
                    _send_validation_email(list_item.title, form.instance)
                except Exception as err:
                    raise Exception(_("Error while sending confirmation email. Please try again later."))
                else:
                    form.save()
            else:
                if request.is_ajax():
                    return JsonResponse({"error": str(form.errors)})
                else:
                    raise Exception('invalid form ' + str(form.errors))
        except django.db.utils.IntegrityError:
            if request.is_ajax():
                return JsonResponse({"error": 'user already subscribed'})
            else:
                messages.error(request, _("You are already subscribed to this newsletter."))
                return redirect('subscriber-management-join', uuid)
        except Exception as err:
            if request.is_ajax():
                return JsonResponse({"error": err})
            else:
                messages.error(request, err)
                return redirect('subscriber-management-join', uuid)
        else:
            if request.is_ajax():
                return JsonResponse({"success": "user successfully subscribed"})
            else:
                return redirect('subscriber-management-join-success', uuid)


class SubscriberJoinSuccess(View):

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        return render(request, "subscriber_join_success.html", locals())


class SubscriberJoinError(View):

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        return render(request, "subscriber_join_error.html", locals())


class SubscriberDeleteView(LoginRequiredMixin, View):

    """
    SubscriberDeleteView manually deletes a subscriber from a list with all it
    associated informations.
    """

    success_message = _(" was successfully delete from this list")

    def get(self, request, uuid, subscriber_uuid):
        subscriber = Subscriber.objects.get(list__uuid=uuid, uuid=subscriber_uuid)
        subscriber.delete()
        messages.success(request, subscriber.email + self.success_message)
        return redirect('subscriber-management-list-subscribers', uuid)


class SubscriberUnsubscribeView(View):
    """
    SubscriberUnsubscribeView unsubscribes a subscriber from a list.
    All it informations will be deleted, the unsubscribe_count of the
    related campaign, if any, will be incremented by 1.
    """

    def get(self, request, uuid, token):

        # Remove subscriber
        try:
            subscriber = Subscriber.objects.get(uuid=uuid, token_unsubscribe=token)
            list = subscriber.list
            subscriber.delete()
            # Increase related campaign's unsubscribe count, if any
            campaign_uuid = request.GET.get('c')
            if campaign_uuid:
                campaign = Campaign.objects.get(uuid=campaign_uuid)
                campaign.unsubscribe_count += 1
                campaign.save()
        except Exception as e:
            raise Http404()
        else:
            return render(request, "subscriber_unsubscribe_success.html", locals())


class SubscriberValidatedView(View):

    """
    SubscriberActivateView activates a subscriber's account
    """

    def get(self, request, uuid, token):
        try:
            subscriber = Subscriber.objects.get(uuid=uuid, token_subscribe=token)
            subscriber.validated = True
            subscriber.save()
            list_item = subscriber.list
        except Exception as e:
            raise Http404()
        else:
            return render(request, "subscriber_validated.html", locals())
        raise Http404()
