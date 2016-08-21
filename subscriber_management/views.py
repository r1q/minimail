from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from subscriber_management.models import List, Subscriber
from subscriber_management.forms import ListForm

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
