from django.contrib import admin

from . import forms as inv_forms, models as inv_models


admin.AdminSite.site_header = "Customized Admin Site Header From Inventory"

admin.site.register(inv_models.Category)
admin.site.register(inv_models.Item)
admin.site.register(inv_models.Order)
admin.site.register(inv_models.Source)
admin.site.register(inv_models.SourceItem)
admin.site.register(inv_models.UnitSize)
