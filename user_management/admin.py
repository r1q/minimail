from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from user_management.models import UserExtend

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserExtendInline(admin.StackedInline):
    model = UserExtend
    can_delete = False
    verbose_name_plural = 'extended'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserExtendInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
