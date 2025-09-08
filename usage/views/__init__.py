from django.views import generic

from .item_usage import ItemUsageCreateView, ItemUsageDetailView, ItemUsageListView, ItemUsageUpdateView
from .usage_by_for_date import UsageByForDateView
from .usage_by_recorded_date import UsageByRecordedDateView
from .usage_group import (
    UsageGroupCreateView, UsageGroupDeleteView, UsageGroupDetailView, UsageGroupListView, UsageGroupUpdateView)
from .usage_on_given_date import UsageOnGivenDateView

class UsageHomepageView(generic.TemplateView):
    template_name = "usage/homepage.html"
