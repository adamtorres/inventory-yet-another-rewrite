import datetime

import dateparser
from django import http, urls
from django.views import generic

from .. import models as u_models


class UsageByRecordedDateView(generic.TemplateView):
    template_name = "usage/usage_by_recorded_date.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        months_back = self.request.GET.get("months_back")
        try:
            months_back = int(months_back)
            if months_back < 1:
                months_back = 1
        except (TypeError, ValueError):
            months_back = 1
        def first_of_month(dt: datetime.date):
            return dt.replace(day=1)

        def back_one_day(dt: datetime.date):
            return dt - datetime.timedelta(days=1)

        def back_one_month(dt: datetime.date):
            return first_of_month(back_one_day(first_of_month(dt)))

        def next_month(dt: datetime.date):
            return first_of_month(first_of_month(dt) + datetime.timedelta(days=32))

        def last_of_month(dt: datetime.date):
            return back_one_day(next_month(dt))
        first_of_current_month = first_of_month(datetime.date.today())
        last_of_current_month = last_of_month(first_of_current_month)
        first_of_last_month = first_of_current_month
        for i in range(months_back):
            first_of_last_month = back_one_month(first_of_last_month)
        context["start_date"] = first_of_last_month
        context["end_date"] = last_of_current_month

        context["totals"] = u_models.ItemUsage.objects.total_recorded_date(
            first_of_last_month, last_of_current_month)
        context["by_date"] = u_models.ItemUsage.objects.group_by_recorded_date(
            first_of_last_month, last_of_current_month)
        return context
