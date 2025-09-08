from django import urls

from . import views as u_views


app_name = "usage"

urlpatterns = [
    urls.path("", u_views.UsageHomepageView.as_view(), name="homepage"),

    urls.path("by_for_date", u_views.UsageByForDateView.as_view(), name="usage_by_for_date"),
    urls.path("by_recorded_date", u_views.UsageByRecordedDateView.as_view(), name="usage_by_recorded_date"),

    urls.path("groups", u_views.UsageGroupListView.as_view(), name="usage_group_list"),
    urls.path("group/new", u_views.UsageGroupCreateView.as_view(), name="usage_group_create"),
    urls.path("group/<int:pk>", u_views.UsageGroupDetailView.as_view(), name="usage_group_detail"),
    urls.path("group/<int:pk>/edit", u_views.UsageGroupUpdateView.as_view(), name="usage_group_update"),
    urls.path("group/<int:pk>/delete", u_views.UsageGroupDeleteView.as_view(), name="usage_group_delete"),

    urls.path("group/<int:group_pk>/item/new", u_views.ItemUsageCreateView.as_view(), name="item_usage_create"),
    urls.path("group/<int:group_pk>/item/<int:pk>", u_views.ItemUsageDetailView.as_view(), name="item_usage_detail"),
    urls.path(
        "group/<int:group_pk>/item/<int:pk>/edit", u_views.ItemUsageUpdateView.as_view(), name="item_usage_update"),

    urls.path("on_date/<slug:given_date>", u_views.UsageOnGivenDateView.as_view(), name="usage_on_given_date"),

]
