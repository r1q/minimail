from django import template
import base64

register = template.Library()

@register.filter(name='decodeURI')
def decodeURI(value):
    try:
        decoded_uri = base64.standard_b64decode(value)
        if len(decoded_uri) < 37:
            return decoded_uri
        return decoded_uri[:37]+bytes("...","utf-8")
    except Exception as err:
        print(err)
        return "<invalid URI> "+value
