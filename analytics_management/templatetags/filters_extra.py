from django import template
import base64

register = template.Library()

@register.filter(name='decodeURI')
def decodeURI(value):
    try:
        return base64.standard_b64decode(value).encode("utf-8")
    except Exception as err:
        print(err)
        return "<invalid URI> "+value+ " " + str(err).encode("utf-8")
