from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from subscriber_management.models import List, Subscriber
from subscriber_management.forms import ListForm, SubscriberForm
import django.db.utils
from django.utils.translation import ugettext as _

class SubscriberListView(ListView):

    model = List
    template_name = 'subscriber_management/template_list.html'

    def get_queryset(self):
        return List.objects.filter(user__id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(SubscriberListView, self).get_context_data(**kwargs)
        return context

class SubscriberCreateView(CreateView):

    model = List
    template_name = 'subscriber_management/template_create.html'
    form_class = ListForm
    success_url="/subscribers/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(SubscriberCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SubscriberCreateView, self).form_valid(form)

class SubscriberListSubscribersView(ListView):

    model = Subscriber
    template_name = 'subscriber_management/template_subscriber_list.html'

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

    def get(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        form = SubscriberForm()
        return render(request, "subscriber_management/template_subscriber_join.html", locals())

    def post(self, request, uuid):
        list_item = List.objects.get(uuid=uuid)
        subscriber_item = Subscriber()
        form = SubscriberForm(request.POST, instance=subscriber_item)
        try:
            if form.is_valid():
                form.instance.list = list_item
                form.save()
        except (django.db.utils.IntegrityError):
            duplicate_error = _('You are already registered to this list')
            return render(request, "subscriber_management/template_subscriber_join.html", locals())
        else:
            return render(request, "subscriber_management/template_subscriber_join_success.html", locals())
