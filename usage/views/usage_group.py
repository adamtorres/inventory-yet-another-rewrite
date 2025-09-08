from django import urls
from django.core.exceptions import MultipleObjectsReturned
from django.views import generic

from .. import models as u_models


class UsageGroupCreateView(generic.CreateView):
    model = u_models.UsageGroup
    fields = ["start_date", "end_date", "name_on_form"]

    def get_success_url(self):
        return urls.reverse("usage:item_usage_create", args=(self.object.id,))


class UsageGroupDeleteView(generic.DeleteView):
    model = u_models.UsageGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.object.total())
        return context

    def get_success_url(self):
        return urls.reverse("usage:usage_group_list")


class UsageGroupDetailView(generic.DetailView):
    model = u_models.UsageGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            next_ug = u_models.UsageGroup.objects.get(form_order=self.object.form_order + 1)
            context["next_usage_group_pk"] = next_ug.pk
        except (u_models.UsageGroup.MultipleObjectsReturned, u_models.UsageGroup.DoesNotExist):
            context["next_usage_group_pk"] = None
        try:
            prev_ug = u_models.UsageGroup.objects.get(form_order=self.object.form_order - 1)
            context["prev_usage_group_pk"] = prev_ug.pk
        except (u_models.UsageGroup.MultipleObjectsReturned, u_models.UsageGroup.DoesNotExist):
            context["prev_usage_group_pk"] = None
        return context

    def get_queryset(self):
        # gets the related items in one query to speed things up.
        qs = super().get_queryset()
        qs = qs.prefetch_related("used_items")
        return qs


class UsageGroupListView(generic.ListView):
    model = u_models.UsageGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usage_groups"] = []
        for obj in context["object_list"]:
            total = obj.total()
            context["usage_groups"].append({
                "ug": obj,
                "total": total["total"],
                "first_date": total["first_date"],
                "last_date": total["last_date"],
            })
        return context


class UsageGroupUpdateView(generic.UpdateView):
    model = u_models.UsageGroup
    fields = ["start_date", "end_date", "name_on_form"]

    def get_queryset(self):
        # gets the related items in one query to speed things up.
        qs = super().get_queryset()
        qs = qs.prefetch_related("used_items")
        return qs

    def get_success_url(self):
        return urls.reverse("usage:usage_group_detail", args=(self.object.id,))
