from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from subscriber_management.models import List, Subscriber
from campaign_management.models import Campaign
from analytics_management.models import OpenRate, ClickRate, OpenRateHourly, \
    SesDeliveryStats, SesComplaintStats, SesBounceStats, SesBounceSoft
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
import json
import hashlib
import sys, os
from datetime import timedelta
import dateutil
from django.db.models import F, FloatField, Sum

ALLOWED_MERGE = ["hour", "day"]
ZERO_IF_NONE = lambda x: 0 if x == None else x

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
        campaign = Campaign.objects.get(
            uuid=campaign_uuid,
            email_list__uuid=list_uuid,
        )
        open_rate_object = OpenRate.objects.filter(list=campaign.email_list, campaign=campaign).first()
        click_rate_object = ClickRate.objects.filter(list=campaign.email_list, campaign=campaign).all()
        ses_delivery_object = SesDeliveryStats.objects.filter(list=campaign.email_list, campaign=campaign).first()
        ses_bounce_object = SesBounceStats.objects.filter(list=campaign.email_list, campaign=campaign).first()
        ses_complaint_object = SesComplaintStats.objects.filter(list=campaign.email_list, campaign=campaign).first()
        time_delta = 0
        if ses_delivery_object:
            time_delta = ses_delivery_object.last.utcnow().timestamp()
            time_delta -= ses_delivery_object.first.utcnow().timestamp()
            time_delta /= int(timedelta/60)
        click_stats_campaign = ClickRate.objects.filter(list=campaign.email_list, campaign=campaign).aggregate(
            total_count=Sum('total_count'),
            unique_count=Sum('unique_count'),
        )
        click_stats_top = dict()
        click_stats_top['total_count'] = 0
        click_stats_top['unique_count'] = 0
        top_links = ClickRate.objects.filter(list=campaign.email_list, campaign=campaign).order_by('-unique_count')[:10]
        for top_link in top_links:
            click_stats_top['total_count'] += top_link.total_count
            click_stats_top['unique_count'] += top_link.unique_count
        return render(request, "campaign.html", locals())


class CampaignApiDateView(LoginRequiredMixin, View):

    @staticmethod
    def initHourPayload(startTime, endTime):
        cursorTime = startTime
        out = list()
        while cursorTime <= endTime or len(out) < 24:
            tmp = dict()
            tmp["date"] = cursorTime
            tmp["total_count"] = 0
            tmp["unique_count"] = 0
            out.append(tmp)
            cursorTime = cursorTime + timedelta(hours=1)
        return out

    @staticmethod
    def initDayPayload(startTime, endTime):
        startTime = startTime.replace(hour=0, minute=0)
        endTime = endTime.replace(hour=0, minute=0)
        cursorTime = startTime
        out = list()
        while cursorTime <= endTime or len(out) < 7:
            tmp = dict()
            tmp["date"] = cursorTime
            tmp["total_count"] = 0
            tmp["unique_count"] = 0
            out.append(tmp)
            cursorTime = cursorTime + timedelta(hours=1)
        return out

    def get(self, request, list_uuid, campaign_uuid, merger):
        if merger not in ALLOWED_MERGE:
            return JsonResponse({"error": _("merge type error.")}, status=400, safe=False)

        try:
            campaign = Campaign.objects.get(
                uuid=campaign_uuid,
                email_list__uuid=list_uuid,
            )
            pStart = OpenRateHourly.objects.filter(list=campaign.email_list, campaign=campaign).order_by('date').first()
            pEnd = OpenRateHourly.objects.filter(list=campaign.email_list, campaign=campaign).order_by('date').last()
            timeSeries = list()
            if merger == "hour":
                timeSeries = CampaignApiDateView.initHourPayload(pStart.date, pEnd.date)
                for timeSerie in timeSeries:
                    out = OpenRateHourly.objects.filter(
                        list=campaign.email_list,
                        campaign=campaign,
                        date__gte=timeSerie["date"],
                        date__lt=timeSerie["date"]+timedelta(hours=1),
                    ).order_by('date').aggregate(
                        total_count=Sum('total_count'),
                        unique_count=Sum('unique_count'),
                    )
                    timeSerie["total_count"] = ZERO_IF_NONE(out["total_count"])
                    timeSerie["unique_count"] = ZERO_IF_NONE(out["unique_count"])
            elif merger == "day":
                timeSeries = CampaignApiDateView.initDayPayload(pStart.date, pEnd.date)
                for timeSerie in timeSeries:
                    out = OpenRateHourly.objects.filter(
                        list=campaign.email_list,
                        campaign=campaign,
                        date__gte=timeSerie["date"],
                        date__lt=timeSerie["date"]+timedelta(days=1),
                    ).order_by('date').aggregate(
                        total_count=Sum('total_count'),
                        unique_count=Sum('unique_count'),
                    )
                    timeSerie["total_count"] = ZERO_IF_NONE(out["total_count"])
                    timeSerie["unique_count"] = ZERO_IF_NONE(out["unique_count"])

        except ValueError as err:
            return JsonResponse({"error": _(err)},  safe=False, status=500)
        else:
            return JsonResponse(timeSeries,  safe=False)


def _gen_analytics_uuid(*args):
    items = list()
    for arg in args:
        items.append(str(arg))
    return hashlib.sha1(":".join(items).encode("utf-8")).hexdigest()


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
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiOpenCountryView(View):

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
            country = json_data.get('country', '')
            _id = _gen_analytics_uuid(list_uuid, campaign_uuid, country)
            defaults = dict()
            defaults["id"] = _id
            defaults["list"] = campaign_object.email_list
            defaults["campaign"] = campaign_object
            defaults["country"] = country
            defaults["total_count"] = 0
            defaults["unique_count"] = 0
            open_rate_obj, created = OpenCountry.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_rate_obj.total_count = int(json_data.get('total', 0))
            open_rate_obj.unique_count = int(json_data.get('unique', 0))
            open_rate_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiOpenDateView(View):

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
            _id = _gen_analytics_uuid(list_uuid, campaign_uuid, json_data.get('date'))
            defaults = dict()
            defaults["id"] = _id
            defaults["list"] = campaign_object.email_list
            defaults["campaign"] = campaign_object
            defaults["date"] = dateutil.parser.parse(json_data.get('date'))
            defaults["total_count"] = 0
            defaults["unique_count"] = 0
            open_date_obj, created = OpenRateHourly.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_date_obj.total_count = int(json_data.get('total', 0))
            open_date_obj.unique_count = int(json_data.get('unique', 0))
            open_date_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
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
            _id = _gen_analytics_uuid(list_uuid, campaign_uuid, json_data.get('uri', ''))
            defaults = dict()
            defaults["id"] = _id
            defaults["list"] = campaign_object.email_list
            defaults["campaign"] = campaign_object
            defaults["uri"] = json_data.get('uri', '')
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
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiSesDeliveryStatsView(View):

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
            defaults["total_count"] = int(json_data.get('total', 0))
            defaults["first"] = dateutil.parser.parse(json_data.get('first'))
            defaults["last"] = dateutil.parser.parse(json_data.get('last'))
            open_rate_obj, created = SesDeliveryStats.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_rate_obj.total_count = int(json_data.get('total', 0))
            open_rate_obj.first = dateutil.parser.parse(json_data.get('first'))
            open_rate_obj.last = dateutil.parser.parse(json_data.get('last'))
            open_rate_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiSesComplaintStatsView(View):

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
            defaults["total_count"] = int(json_data.get('total', 0))
            open_rate_obj, created = SesComplaintStats.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_rate_obj.total_count = int(json_data.get('total', 0))
            open_rate_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiSesBounceStatsView(View):

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
            defaults["soft_count"] = int(json_data.get('soft', 0))
            defaults["hard_count"] = int(json_data.get('hard', 0))
            open_rate_obj, created = SesBounceStats.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            open_rate_obj.soft_count = int(json_data.get('soft', 0))
            open_rate_obj.hard_count = int(json_data.get('hard', 0))
            open_rate_obj.save()
        except ObjectDoesNotExist:
            raise Http404
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiSesBounceSoftView(View):

    def post(self, request, list_uuid, campaign_uuid):
        if request.META.get('HTTP_X_ANALYTICS_KEY', '') != settings.ANALYTICS_KEY:
            return HttpResponse(status=403)
        campaign_object = None
        try:
            # campaign_object = Campaign.objects.get(
            #     uuid=campaign_uuid,
            #     email_list__uuid=list_uuid,
            # )
            json_data = json.loads(request.body.decode('utf-8'))
            subscriber_uuid = json_data.get('subscriber', '')
            _id = _gen_analytics_uuid(list_uuid, campaign_uuid, subscriber_uuid)
            defaults = dict()
            defaults["id"] = _id
            defaults["list_uuid"] = list_uuid
            defaults["campaign_uuid"] = campaign_uuid
            defaults["subscriber_uuid"] = subscriber_uuid
            defaults["bounce_type"] = json_data.get('subtype', '')
            obj, created = SesBounceSoft.objects.get_or_create(
                id=_id,
                defaults=defaults
            )
            obj.bounce_type = json_data.get('subtype', '')
            obj.save()
        except ObjectDoesNotExist:
            raise Http404
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ApiSesSuppressSubscribersView(View):

    def post(self, request, list_uuid):
        if request.META.get('HTTP_X_ANALYTICS_KEY', '') != settings.ANALYTICS_KEY:
            return HttpResponse(status=403)
        campaign_object = None
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            subscribers_list = json_data.get('subscribers', [])
            Subscriber.objects.filter(
                list__uuid=list_uuid,
                uuid__in=subscribers_list
            ).delete()
        except ObjectDoesNotExist:
            raise Http404
        except ValueError as er:
            print(er)
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=204)
