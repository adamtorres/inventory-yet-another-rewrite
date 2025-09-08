import datetime

import dateparser
from django import http, urls
from django.views import generic

from .. import models as u_models


class UsageByForDateView(generic.TemplateView):
    template_name = "usage/usage_by_for_date.html"

    def calendar_grid(self, start_date, end_date, exclude_recorded=False):
        by_category_qs = u_models.ItemUsage.objects.group_by_for_date_and_category(
            start_date, for_date_last=end_date, exclude_recorded=exclude_recorded)
        weeks = {}
        for i in by_category_qs:
            # year*100+week to get 202401-202452 and 202501-202552.  Makes it so the calendar works over the divide.
            week = (i["for_date"].isocalendar()[0] * 100) + i["for_date"].isocalendar()[1]
            weekday = i["for_date"].isocalendar()[2]
            if week not in weeks:
                sunday_of_week = i["for_date"] - datetime.timedelta(days=weekday)
                # initialize a week with the dates
                weeks[week] = [{"date": sunday_of_week + datetime.timedelta(days=i), "empty": True} for i in range(7)]
            # There's exactly zero or one of each category so no worry of overwriting.
            weeks[week][weekday][i["category"]] = i
            weeks[week][weekday].pop("empty", None)
        if not weeks:
            return None
        first_week = min(weeks.keys())
        last_week = max(weeks.keys())
        return [weeks.get(week, [None, None, None, None, None, None, None]) for week in range(first_week, last_week+1)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exclude_recorded = self.request.GET.get("exclude_recorded") == "yes"
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
        context["totals"] = u_models.ItemUsage.objects.total_for_date(
            first_of_last_month, last_of_current_month, exclude_recorded=exclude_recorded)
        context["by_date"] = u_models.ItemUsage.objects.group_by_for_date(
            first_of_last_month, last_of_current_month, exclude_recorded=exclude_recorded)
        context["calendar_grid"] = self.calendar_grid(
            first_of_last_month, last_of_current_month, exclude_recorded=exclude_recorded)
        return context

    def post(self, request, *args, **kwargs):
        try:
            start_date = dateparser.parse(request.POST.get("start_date")).date()
            end_date = dateparser.parse(request.POST.get("end_date")).date()
        except AttributeError:
            return http.HttpResponseRedirect(urls.reverse("usage:usage_by_for_date"))
        u_models.ItemUsage.objects.mark_as_recorded(start_date, end_date)
        return http.HttpResponseRedirect(urls.reverse("usage:usage_by_for_date") + "?" + request.GET.urlencode())
