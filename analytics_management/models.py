from django.db import models
from analytics_management.models_pixou import \
    PixouOpenRate, PixouClickRate, PixouSesRate

# Create your models here.
class OpenRate(PixouOpenRate):

    def avg(self):
        if self.total == 0:
            return 0
        return int(self.uniq / self.total)*100

class ClickRate(PixouClickRate):

    def avg(self):
        if self.total == 0:
            return 0
        return int(self.uniq / self.total)*100

class SesRate(PixouSesRate):
    pass
