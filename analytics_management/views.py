from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from subscriber_management.models import List
from campaign_management.models import Campaign
from analytics_management.models import OpenRate, ClickRate, SesRate

class HomeView(LoginRequiredMixin, View):

    def get(sefl, request):
        object_list = List.objects.filter(user=request.user)
        return render(request, "home.html", locals())

class ListView(LoginRequiredMixin, View):

    def get(sefl, request, uuid):
        list_object = List.objects.get(uuid=uuid)
        object_list = Campaign.objects.filter(email_list__uuid=uuid)
        return render(request, "list.html", locals())

class CampaignView(LoginRequiredMixin, View):

    def get(sefl, request, list_uuid, campaign_uuid):
        campaign_object = Campaign.objects.get(
            uuid=campaign_uuid,
            email_list__uuid=list_uuid,
        )
        open_rate_object = OpenRate.objects.using('pixou').get(list=list_uuid, campaign=campaign_uuid)
        click_rate_object = ClickRate.objects.using('pixou').get(list=list_uuid, campaign=campaign_uuid)
        ses_rate_object = SesRate.objects.using('pixou').get(list=list_uuid, campaign=campaign_uuid)
        return render(request, "campaign.html", locals())
