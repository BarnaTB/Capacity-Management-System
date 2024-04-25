from django.contrib import admin

from accounts.models import DeveloperProfile, User

admin.site.register(User)
admin.site.register(DeveloperProfile)
