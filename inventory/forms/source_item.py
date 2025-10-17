from django import forms

from inventory import models as inv_models
from inventory.forms import widgets as inv_widgets


class SourceItemForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=inv_models.Item.objects.all(), widget=inv_widgets.ModelPickerWidget)
    class Meta:
        model = inv_models.SourceItem
        fields = [
            "source", "item_number", "extra_number", "cryptic_name", "expanded_name", "common_name",
            "item", "brand", "source_category", "unit_size", "unit_amount", "unit_amount_text", "subunit_size",
            "subunit_amount", "subunit_amount_text", "active", "quantity", "allow_split_pack"
        ]


class SourceItemTestDropDownForm(forms.Form):
    # template_name_ div, p, table, ul, label "django/forms/___.html"
    # template_name_table = "inventory/forms/source_item_test_drop_down_form_table.html"
    search_wider = forms.CharField(widget=inv_widgets.ModelPickerWidget(attrs={"placeholder": "name or code"}))
