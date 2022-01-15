from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.UserProfile)
admin.site.register(models.Plans)
admin.site.register(models.UserPlans)
