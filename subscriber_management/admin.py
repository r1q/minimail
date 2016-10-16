from django.contrib import admin
from subscriber_management.models import Subscriber, List

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'list', 'validated',)
    search_fields = ('email',)

class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'from_email', 'from_email_verified',)
    search_fields = ('name',)

admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(List, ListAdmin)
