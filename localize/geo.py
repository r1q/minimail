from geolite2 import geolite2
from localize import timezone

reader = geolite2.reader()

def get_timezone(ip):
    t = get_country_code(ip)
    if t == '':
        return 'GMT'
    return timezone.iso_code_to_timezone(t)

def get_country_code(ip):
    match = reader.get(ip)
    if match is None:
        return ''
    return match['registered_country']['iso_code']
