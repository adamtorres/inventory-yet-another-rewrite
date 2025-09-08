from django.contrib import admin

from . import models as u_models


admin.AdminSite.site_header = "Usage Form Site Admin"


admin.site.register(u_models.ItemUsage)
admin.site.register(u_models.UsageGroup)
