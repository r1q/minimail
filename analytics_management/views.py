from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from subscriber_management.models import List
from campaign_management.models import Campaign
from analytics_management.models import OpenRate, ClickRate, SesRate
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
import json
import hashlib
import sys, os


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
        return render(request, "campaign.html", locals())

def _gen_analytics_uuid(*args):
    return hashlib.sha1(":".join(args).encode("utf-8")).hexdigest()

@method_decorator(csrf_exempt, name='dispatch')
class ApiOpenRateView(View):

    def post(self, request, list_uuid, campaign_uuid):
        if request.META.get('HTTP_X_ANALYTICS_KEY', '') != settings.ANALYTICS_KEY:
            return HttpResponse(status=403)
        campaign_object = None

        try:
            campaign_object = Campaign.objects.get(
                uuid=campaign_uuid,
                email_list__uuid=list_uuid,
            )
            json_data = json.loads(request.body.decode('utf-8'))
            _id = _gen_analytics_uuid(list_uuid, campaign_uuid)
            defaults = dict()
            defaults["id"] = _id
            defaults["list"] = campaign_object.email_list
            defaults["campaign"] = campaign_object
            defaults["total_count"] = 0
            defaults["unique_count"] = 0
            open_rate_obj, created = OpenRate.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_rate_obj.total_count = int(json_data.get('total', 0))
            open_rate_obj.unique_count = int(json_data.get('unique', 0))
            open_rate_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiClickRateView(View):

    def post(self, request, list_uuid, campaign_uuid):
        if request.META.get('HTTP_X_ANALYTICS_KEY', '') != settings.ANALYTICS_KEY:
            return HttpResponse(status=403)
        campaign_object = None

        try:
            campaign_object = Campaign.objects.get(
                uuid=campaign_uuid,
                email_list__uuid=list_uuid,
            )
            json_data = json.loads(request.body.decode('utf-8'))
            _id = _gen_analytics_uuid(list_uuid, campaign_uuid)
            defaults = dict()
            defaults["id"] = _id
            defaults["list"] = campaign_object.email_list
            defaults["campaign"] = campaign_object
            defaults["total_count"] = 0
            defaults["unique_count"] = 0
            open_rate_obj, created = ClickRate.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_rate_obj.total_count = int(json_data.get('total', 0))
            open_rate_obj.unique_count = int(json_data.get('unique', 0))
            open_rate_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiSesRateView(View):

    def post(self, request, list_uuid, campaign_uuid):
        if request.META.get('HTTP_X_ANALYTICS_KEY', '') != settings.ANALYTICS_KEY:
            return HttpResponse(status=403)
        campaign_object = None

        try:
            campaign_object = Campaign.objects.get(
                uuid=campaign_uuid,
                email_list__uuid=list_uuid,
            )
            json_data = json.loads(request.body.decode('utf-8'))
            _id = _gen_analytics_uuid(list_uuid, campaign_uuid)
            defaults = dict()
            defaults["id"] = _id
            defaults["list"] = campaign_object.email_list
            defaults["campaign"] = campaign_object
            defaults["delivery_count"] = 0
            defaults["bounce_count"] = 0
            defaults["complaint_count"] = 0
            open_rate_obj, created = SesRate.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_rate_obj.delivery_count = int(json_data.get('delivery', 0))
            open_rate_obj.bounce_count = int(json_data.get('bounce', 0))
            open_rate_obj.complaint_count = int(json_data.get('complaint', 0))
            open_rate_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        else:
            return HttpResponse(status=204)
