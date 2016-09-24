"""
view.py contains all the logic for subscriber lists and associated
subscribers.
"""

import csv
from datetime import datetime
from tempfile import NamedTemporaryFile
import pytz
import json

from localize import geo, timezone

import django.db.utils
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.http import Http404
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt

from subscriber_management.models import List, Subscriber
from subscriber_management.forms import ListForm, SubscriberForm, \
    ListSettings, ListNewsletterHomepage

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

VALIDATION_EMAIL = _("""
{}

Click this link to confirm your subscription:
{}

If you didn't subscribe, you can ignore this email. You won't be subscribed if you don't click the link above.


— Sent with Minimail
""")

def send_validation_email(list_name, subscriber):
    send_mail(
        "{}: {}".format(list_name, _('Please Confirm Subscription')), # Subject
        VALIDATION_EMAIL.format(list_name, subscriber.validation_link()), # Text email
        # TODO: Replace that with user's verified From: email
        'hi@fullweb.io', # From: email
        [subscriber.email], # To:
        fail_silently=False,
    )


class SubscriberListView(LoginRequiredMixin, ListView):

    """
    SubscriberListView display subscribers lists that belongs to a user.
    """

    model = List
    template_name = 'list_list.html'

    def get_queryset(self):
        return List.objects.filter(user__id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(SubscriberListView, self).get_context_data(**kwargs)
        return context


class SubscriberListCreateView(LoginRequiredMixin, CreateView):

    """
    SubscriberCreateView create a new empty list of subscribers.
    """

    model = List
    template_name = 'list_create.html'
    form_class = ListForm
    success_url = "/subscribers/"
    success_message = _(" was successfully created")

    def form_valid(self, form):
        messages.success(self.request, form.instance.name + self.success_message)
        form.instance.user = self.request.user
        return super(SubscriberListCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SubscriberListCreateView, self).form_valid(form)


class SubscriberListSettingsView(LoginRequiredMixin, View):

    """
    SubscriberListSettingsView updates an existing list for subscribers.
    """

    success_message = _(" was successfully updated")

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        form_object = ListSettings(instance=list_item)
        return render(request, "list_settings.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        form_object = ListSettings(request.POST, instance=list_item)
        if form_object.is_valid():
            messages.success(self.request, form_object.instance.name + self.success_message)
            form_object.save()
            return redirect('subscriber-management-list-settings', uuid)
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
            messages.success(self.request, form_object.instance.name + self.success_message)
            form_object.save()
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
        messages.success(request, list_item.name + self.success_message)
        Subscriber.objects.filter(list__id=list_item.id).delete()
        list_item.delete()
        return redirect('subscriber-management-list')


class SubscriberListImportCSV(LoginRequiredMixin, View):

    """
    SubscriberListImportCSV import and parse a csv file from mailchimp.
    Subscribers are automatically considered as 'validated'.
    """

    success_message = _(" subscriber(s) imported")

    def save_user(self, list_item, row):
        try:
            new_subscriber = Subscriber()
            new_subscriber.list = list_item
            new_subscriber.email = row['Email Address']
            name_info = row['Name'].split(' ')
            if len(name_info) == 2:
                new_subscriber.first_name = name_info[0]
                new_subscriber.last_name = name_info[1]
            elif len(name_info) == 1:
                new_subscriber.first_name = name_info[0]
            else:
                pass
            if 'TIMEZONE' in row and row['TIMEZONE'] != "":
                new_subscriber.timezone = row['TIMEZONE']
            else:
                new_subscriber.timezone = "GMT"
            new_subscriber.country = timezone.timezone_to_iso_code(new_subscriber.timezone)
            if 'OPTIN_IP' in row and row['OPTIN_IP'] != "":
                new_subscriber.ip_subscribe = row['OPTIN_IP']
                print("test", geo.get_country_code(row['OPTIN_IP']))
            if 'CONFIRM_IP' in row and row['CONFIRM_IP'] != "":
                new_subscriber.ip_validate = row['CONFIRM_IP']
            new_subscriber.validated = True
            new_subscriber.extra = json.dumps(row)
            new_subscriber.save()
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        return render(request, "list_import.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        csv_file = request.FILES['csv_file']
        tmp = NamedTemporaryFile('wb')
        tmp.write(csv_file.read())

        save_count = 0
        with open(tmp.name, 'r') as f:
            reader = csv.DictReader(f)
            print('file names', reader.fieldnames)
            for row in reader:
                if row['Email Address'] == '':
                    continue
                if self.save_user(list_item, row) == True:
                    save_count += 1
        tmp.close()
        messages.success(request, str(save_count) + self.success_message)
        return redirect('subscriber-management-list-subscribers', uuid)


class SubscriberListSubscribersView(LoginRequiredMixin, ListView):

    """
    SubscriberListSubscribersView list all the subscribers associated to a list.
    """

    model = Subscriber
    template_name = 'subscriber_list.html'

    def get_queryset(self):
        list_uuid = self.kwargs['uuid']
        return Subscriber.objects.filter(list__uuid=list_uuid,validated=True).order_by('email')

    def get_context_data(self, **kwargs):
        context = super(SubscriberListSubscribersView, self).get_context_data(**kwargs)
        list_uuid = self.kwargs['uuid']
        list_item = List.objects.get(uuid=list_uuid)
        context['list_item'] = list_item
        context['list'] = list_item
        context['total_count'] = context['object_list'].count()
        paginator = Paginator(context['object_list'], 100)

        page = self.request.GET.get('page')
        try:
            context['object_list'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['object_list'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['object_list'] = paginator.page(paginator.num_pages)
        context['paginator'] = paginator
        context['page_nums'] = range(1, paginator.num_pages+1)

        return context


class SubscriberListSubscribersBulkView(LoginRequiredMixin, View):

    def post(self, request, uuid):
        print(request.POST)
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
        form = SubscriberForm()
        return render(request, "subscriber_join.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        if list_item.signup_token() in request.POST:
            if request.POST[list_item.signup_token()] != "":
                if request.is_ajax():
                    return JsonResponse({"error": _('invalid form')})
                else:
                    messages.error(request, _("invalid form"))
                    return redirect('subscriber-management-join-error', uuid)
        else:
            if request.is_ajax():
                return JsonResponse({"error": _("validation field required")})
            else:
                messages.error(request, _("validation field required"))
                return redirect('subscriber-management-join-error', uuid)

        subscriber_item = Subscriber()
        form = SubscriberForm(request.POST, instance=subscriber_item)
        try:
            if form.is_valid():
                form.instance.list = list_item
                form.instance.ip = self._get_client_ip(request)
                form.instance.country = self._get_country_from_ip(request)
                form.instance.timezone = geo.get_timezone(form.instance.ip)
                form.instance.user_agent = request.META.get('HTTP_USER_AGENT', '')
                form.instance.accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
                form.save()
                send_validation_email(list_item.title, form.instance)
            else:
                if request.is_ajax():
                    return JsonResponse({"error": _('invalid form')})
                else:
                    raise Exception('invalid form')
        except django.db.utils.IntegrityError:
            duplicate_error = _('You are already registered to this list')
            if request.is_ajax():
                return JsonResponse({"error": duplicate_error})
            else:
                messages.error(request, duplicate_error)
                return redirect('subscriber-management-join-error', uuid)
        except Exception as err:
            if request.is_ajax():
                return JsonResponse({"error": err})
            else:
                messages.error(request, err)
                return redirect('subscriber-management-join-error', uuid)
        else:
            if request.is_ajax():
                if list_item.success_template == "":
                    return JsonResponse({"success": _("sucess")})
                else:
                    return JsonResponse({"success": list_item.success_template})
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
        messages.success(request, subscriber.email + self.success_message)
        subscriber.delete()
        return redirect('subscriber-management-list-subscribers', uuid)


class SubscriberUnsubscribeView(View):

    """
    SubscriberUnsubscribeView allows a subscriber to unsubscribe from a list.
    All it informations will be deleted.
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(SubscriberUnsubscribeView, self).dispatch(*args, **kwargs)

    def get(self, request, uuid, token):
        try:
            subscriber = Subscriber.objects.get(uuid=uuid, token_unsubscribe=token)
        except Exception as e:
            raise Http404()
        else:
            list = subscriber.list
            return render(request, "subscriber_unsubscribe.html", locals())
        raise Http404()

    def post(self, request, uuid, token):
        try:
            subscriber = Subscriber.objects.get(uuid=uuid, token_unsubscribe=token)
            list = subscriber.list
            subscriber.delete()
        except Exception as e:
            raise Http404()
        else:
            return render(request, "subscriber_unsubscribe_success.html", locals())
        raise Http404()


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
