from django.contrib import admin
from subscriber_management.models import Subscriber, List

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'list', 'validated')
    search_fields = ('email',)

admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(List)
