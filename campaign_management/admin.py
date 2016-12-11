from django.contrib import admin

from campaign_management.models import Campaign

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('email_subject','is_sent', 'email_list', 'author',)
    readonly_fields = ('uuid',)

admin.site.register(Campaign, CampaignAdmin)
