import pytz
import datetime as DT
utcnow = DT.datetime.utcnow()

canonical = dict()
for name in pytz.common_timezones:
    tzone = pytz.timezone(name)
    try:
        dstoffset = tzone.dst(utcnow, is_dst=False)
    except TypeError:
        # pytz.utc.dst does not have a is_dst keyword argument
        dstoffset = tzone.dst(utcnow)
    if dstoffset == DT.timedelta(0):
        # utcnow happens to be in a non-DST period
        canonical[name] = tzone.localize(utcnow, is_dst=False).strftime('%z')
    else:
        # step through the transition times until we find a non-DST datetime
        date = utcnow
        while True:
            date = date - DT.timedelta(days=1)
            dstoffset = tzone.dst(date, is_dst=False)
            if dstoffset == DT.timedelta(0):
                canonical[name] = (tzone.localize(date, is_dst=False)
                                   .strftime('%z'))
                break

# for name, utcoffset in canonical.items():
#     print('{} --> {}'.format(name, utcoffset))

TIMEZONES_HUMAN = dict()
TIMEZONE_LIST = list()

timezone_country = {}
for countrycode in pytz.country_timezones:
    timezones = pytz.country_timezones[countrycode]
    for timezone in timezones:
        timezone_country[timezone] = countrycode

k = canonical.keys()
for name in sorted(k):
    utcoffset = canonical[name]
    TIMEZONE_LIST.append(name)
    TIMEZONES_HUMAN[name] = '{} ({})'.format(name, utcoffset)

def timezone_offset(name):
    tzone = pytz.timezone(name)
    try:
        dstoffset = tzone.dst(utcnow, is_dst=False)
    except TypeError:
        # pytz.utc.dst does not have a is_dst keyword argument
        dstoffset = tzone.dst(utcnow)
    if dstoffset == DT.timedelta(0):
        # utcnow happens to be in a non-DST period
        return tzone.localize(utcnow, is_dst=False).strftime('%z')
    else:
        # step through the transition times until we find a non-DST datetime
        date = utcnow
        while True:
            date = date - DT.timedelta(days=1)
            dstoffset = tzone.dst(date, is_dst=False)
            if dstoffset == DT.timedelta(0):
                return tzone.localize(date, is_dst=False).strftime('%z')

def human_timezone(name):
    return '{} ({})'.format(name, timezone_offset(name))

def iso_code_to_timezone(iso):
    out = pytz.country_timezones(iso)
    if len(out) == 0:
        return ''
    return out[0]

def timezone_to_iso_code(tz):
    if tz in timezone_country:
        return timezone_country[tz]
    return ''
