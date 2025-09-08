from django import forms

from .. import models as u_models


class ItemUsageForm(forms.ModelForm):
    class Meta:
        model = u_models.ItemUsage
        fields = [
            "usage_group", "for_dow", "for_other_dow", "donated", "estimate", "price", "description", "category",
            "comment", "quantity", "used_size", "meal_part"
        ]

    def save(self, commit=True):
        self.instance.set_for_date()
        obj = super().save(commit=commit)
        return obj
