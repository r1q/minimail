from django.conf import settings

def settings_base_url(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'BASE_URL': settings.BASE_URL}
