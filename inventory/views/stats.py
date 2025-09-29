from django.views import generic

from .. import models as inv_models
from user import mixins as u_mixins


class StatsView(u_mixins.UserAccessMixin, generic.TemplateView):
    template_name = "inventory/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_stats"] = inv_models.Order.objects.get_stats()
        context["totals_by_month"] = inv_models.OrderLineItem.objects.totals_by_month()
        pivoted_headers, pivoted_data = inv_models.OrderLineItem.objects.pivoted_totals_by_month_and_source()
        context["pivoted_totals_by_month_and_source_headers"] = pivoted_headers
        context["pivoted_totals_by_month_and_source"] = pivoted_data
        pivoted_headers, pivoted_data = inv_models.OrderLineItem.objects.pivoted_totals_by_month_and_category()
        context["pivoted_totals_by_month_and_category_headers"] = pivoted_headers
        context["pivoted_totals_by_month_and_category"] = pivoted_data
        return context
