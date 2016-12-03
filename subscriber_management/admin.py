from django.contrib import admin
from subscriber_management.models import Subscriber, List

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email','uuid', 'list', 'validated',)
    readonly_fields = ('token_unsubscribe', 'token_subscribe',)
    search_fields = ('email',)

class ListAdmin(admin.ModelAdmin):
    list_display = ('name','uuid',  'title', 'from_email', 'from_email_verified',)
    readonly_fields = ('uuid',)
    search_fields = ('name',)

admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(List, ListAdmin)
