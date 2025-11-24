from django.contrib import admin

from . import models as t_models


class LocationReadingFilter(admin.SimpleListFilter):
    title = 'Location'
    parameter_name = 'location_reading_filter'

    def lookups(self, request, model_admin):
        # Define the options for the filter
        location_names = model_admin.model.get_all_locations()
        return [(n, n) for n in location_names]

    def queryset(self, request, queryset):
        # Apply filtering based on the selected option
        if self.value():
            return queryset.filter(location_readings__has_key=self.value())
        return queryset


class TemperatureAdmin(admin.ModelAdmin):
    list_filter = [LocationReadingFilter, ]


admin.site.register(t_models.Temperature, TemperatureAdmin)
