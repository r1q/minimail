from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
import django.db.utils
from django.utils.translation import ugettext as _
from django.contrib import messages

from subscriber_management.models import List, Subscriber
from subscriber_management.forms import ListForm, SubscriberForm


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
    success_message = " was successfully created"

    def form_valid(self, form):
        messages.success(self.request, form.instance.name + self.success_message)
        form.instance.user = self.request.user
        return super(SubscriberCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SubscriberCreateView, self).form_valid(form)


class SubscriberListDeleteView(View):

    success_message = " was successfully deleted"

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        messages.success(request, list_item.name + self.success_message)
        Subscriber.objects.filter(list__id=list_item.id).delete()
        list_item.delete()
        return redirect('subscriber-management-list')


class SubscriberListSubscribersView(ListView):

    model = Subscriber
    template_name = 'subscriber_list.html'

    def get_queryset(self):
        list_uuid = self.kwargs['uuid']
        return Subscriber.objects.filter(list__uuid=list_uuid)

    def get_context_data(self, **kwargs):
        context = super(SubscriberListSubscribersView, self).get_context_data(**kwargs)
        list_uuid = self.kwargs['uuid']
        list_item = List.objects.get(uuid=list_uuid)
        context['list'] = list_item
        return context


class SubscribeJoin(View):

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
