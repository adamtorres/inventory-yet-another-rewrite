from django import urls
from django.views import generic

from .. import forms as u_forms, models as u_models


class ItemUsageCreateView(generic.CreateView):
    model = u_models.ItemUsage
    form_class = u_forms.ItemUsageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_pk"] = self.kwargs['group_pk']
        ug = u_models.UsageGroup.objects.get(id=self.kwargs['group_pk'])
        context["siblings"] = ug.used_items.all()
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['usage_group'] = self.kwargs['group_pk']
        return initial

    def get_success_url(self):
        # Creating an item usage is usually done when entering a form.  Save a click, redirect to creating another.
        return urls.reverse("usage:item_usage_create", args=(self.object.usage_group.id,))


class ItemUsageDetailView(generic.DetailView):
    model = u_models.ItemUsage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_pk"] = self.kwargs['group_pk']
        return context

    def get_queryset(self):
        # gets the related items in one query to speed things up.
        qs = super().get_queryset()
        # Get the siblings to show on the page.
        qs = qs.prefetch_related("usage_group", "usage_group__used_items")
        return qs


class ItemUsageListView(generic.ListView):
    model = u_models.ItemUsage


class ItemUsageUpdateView(generic.UpdateView):
    model = u_models.ItemUsage
    form_class = u_forms.ItemUsageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_pk"] = self.kwargs['group_pk']
        ug = u_models.UsageGroup.objects.get(id=self.kwargs['group_pk'])
        context["siblings"] = ug.used_items.all()
        return context

    def get_queryset(self):
        # gets the related items in one query to speed things up.
        qs = super().get_queryset()
        qs = qs.prefetch_related("usage_group__used_items")
        return qs

    def get_success_url(self):
        if "save_and_edit_next_item" in self.request.POST:
            use_next_ui = False
            for ui in self.object.usage_group.used_items.all():
                if use_next_ui:
                    return urls.reverse("usage:item_usage_update", args=(self.object.usage_group.id, ui.id))
                if ui.id == self.object.id:
                    use_next_ui = True
            # If we get here, there is no next ui in this usage group.  Move to next usage group and start on its ui.
            try:
                next_ug = u_models.UsageGroup.objects.get(form_order=self.object.usage_group.form_order + 1)
                # Can have no items?  Not the way the current data was imported.  Don't worry about it for now.
                next_ugs_first_ui = next_ug.used_items.all().first()
                return urls.reverse("usage:item_usage_update", args=(next_ug.id, next_ugs_first_ui.id))
            except (u_models.UsageGroup.MultipleObjectsReturned, u_models.UsageGroup.DoesNotExist):
                # DoesNotExist is not an error.  Just the end of the forms.
                # MultipleObjectsReturned is strange but not something I want to deal with in a stop-gap application.
                pass
        return urls.reverse("usage:usage_group_detail", args=(self.object.usage_group.id,))
