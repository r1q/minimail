from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.http import Http404
import django.db.utils
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import csv
from tempfile import NamedTemporaryFile
from datetime import datetime
import pytz

from subscriber_management.models import List, Subscriber
from subscriber_management.forms import ListForm, SubscriberForm

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class SubscriberListView(ListView):

    model = List
    template_name = 'list_list.html'

    def get_queryset(self):
        return List.objects.filter(user__id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(SubscriberListView, self).get_context_data(**kwargs)
        return context


class SubscriberCreateView(CreateView):

    model = List
    template_name = 'list_create.html'
    form_class = ListForm
    success_url = "/subscribers/"
    success_message = _(" was successfully created")

    def form_valid(self, form):
        messages.success(self.request, form.instance.name + self.success_message)
        form.instance.user = self.request.user
        return super(SubscriberCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SubscriberCreateView, self).form_valid(form)


class SubscriberListUpdateView(UpdateView):

    model = List
    template_name = 'list_update.html'
    fields = ['image', 'name', 'title', 'description', 'url', 'success_template']
    success_url = "/subscribers/"
    success_message = _(" was successfully updated")

    def form_valid(self, form):
        messages.success(self.request, form.instance.name + self.success_message)
        print(form.instance)
        return super(SubscriberListUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SubscriberListUpdateView, self).form_invalid(form)


class SubscriberListDeleteView(View):

    success_message = " was successfully deleted"

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        messages.success(request, list_item.name + self.success_message)
        Subscriber.objects.filter(list__id=list_item.id).delete()
        list_item.delete()
        return redirect('subscriber-management-list')


class SubscriberListImportCSV(View):

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
            if row['TIMEZONE'] != '':
                new_subscriber.timezone_str = row['TIMEZONE']
                d = datetime.now(pytz.timezone(row['TIMEZONE']))
                new_subscriber.timezone = d.utcoffset().total_seconds()/60/60
            else:
                new_subscriber.timezone_str = 'UTC'
                new_subscriber.timezone = 0

            new_subscriber.member_rating = int(row['MEMBER_RATING']) / 5
            if row['OPTIN_TIME'] != '':
                new_subscriber.optin_time = datetime.strptime(row['OPTIN_TIME'], DATE_FORMAT)
            new_subscriber.optin_ip = row['OPTIN_IP']
            new_subscriber.ip = row['OPTIN_IP']
            if row['CONFIRM_TIME'] != '':
                new_subscriber.confim_time = datetime.strptime(row['CONFIRM_TIME'], DATE_FORMAT)
            new_subscriber.confim_ip = row['CONFIRM_IP']
            if row['LATITUDE'] != '':
                new_subscriber.latitude = float(row['LATITUDE'])
            if row['LONGITUDE'] != '':
                new_subscriber.longitude = float(row['LONGITUDE'])
            new_subscriber.cc = row['CC']
            new_subscriber.region = row['REGION']
            new_subscriber.notes = row['NOTES']
            new_subscriber.validated = True
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




class SubscriberListSubscribersView(ListView):

    model = Subscriber
    template_name = 'subscriber_list.html'

    def get_queryset(self):
        list_uuid = self.kwargs['uuid']
        return Subscriber.objects.filter(list__uuid=list_uuid).order_by('email')

    def get_context_data(self, **kwargs):
        context = super(SubscriberListSubscribersView, self).get_context_data(**kwargs)
        list_uuid = self.kwargs['uuid']
        list_item = List.objects.get(uuid=list_uuid)
        context['list'] = list_item
        return context


class SubscriberJoin(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(SubscriberJoin, self).dispatch(*args, **kwargs)

    def _get_client_ip(self, req):
        return req.META.get('HTTP_X_FORWARDED_FOR') if req.META.get('HTTP_X_FORWARDED_FOR') else req.META.get('REMOTE_ADDR')

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        form = SubscriberForm()
        return render(request, "subscriber_join.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        subscriber_item = Subscriber()
        form = SubscriberForm(request.POST, instance=subscriber_item)
        try:
            if form.is_valid():
                form.instance.list = list_item
                form.instance.ip = self._get_client_ip(request)
                form.instance.user_agent = request.META.get('HTTP_USER_AGENT', '')
                form.instance.accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
                form.save()
            else:
                print(form)
                raise Exception('invalid form')
        except (django.db.utils.IntegrityError):
            duplicate_error = _('You are already registered to this list')
            return render(request, "subscriber_join.html", locals())
        except Exception as err:
            print(err)
            return render(request, "subscriber_join.html", locals())
        else:
            return render(request, "subscriber_join_success.html", locals())

class SubscriberDelete(View):

    success_message = _(" was successfully delete from this list")

    def get(self, request, uuid, subscriber_uuid):
        subscriber = Subscriber.objects.get(list__uuid=uuid, uuid=subscriber_uuid)
        messages.success(request, subscriber.email + self.success_message)
        subscriber.delete()
        return redirect('subscriber-management-list-subscribers', uuid)
