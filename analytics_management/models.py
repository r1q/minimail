from django.db import models
from analytics_management.models_pixou import \
    PixouOpenRate, PixouClickRate, PixouSesRate

def _get_ses_stats(list_uuid:str, campaign_uuid:str):
    return SesRate.objects.using('pixou').get(
        list=list_uuid,
        campaign=campaign_uuid,
    )

# Create your models here.
class OpenRate(PixouOpenRate):

    def avg(self):
        ses_stats = _get_ses_stats(self.list, self.campaign)
        if ses_stats.delivery == 0:
            return 0
        return int((float(self.uniq) / float(ses_stats.delivery)) * 100)

class ClickRate(PixouClickRate):
    pass

class SesRate(PixouSesRate):
    pass
