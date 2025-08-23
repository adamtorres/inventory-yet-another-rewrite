import logging

from django import forms

from . import grouped_model_choice
from inventory import models as inv_models


logger = logging.getLogger(__name__)


class CustomSelect(forms.Select):
    template_name = "inventory/widgets/item_select.html"
    option_template_name = "inventory/widgets/item_select_option.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.critical("CustomSelect!")


class ConversionForm(forms.ModelForm):
    item = grouped_model_choice.GroupedModelChoiceField(
        inv_models.Item.objects.ingredients(),
        choices_groupby="category"
    )
    # ('group_label', [('value1', 'display_label1'), ('value2', 'display_label2')])
    from_unit = forms.ModelChoiceField(inv_models.UnitSize.objects.all())
    to_unit = forms.ModelChoiceField(inv_models.UnitSize.objects.all())
    multiplier = forms.DecimalField(max_digits=9, decimal_places=4)

    class Meta:
        model = inv_models.Conversion
        fields = ["item", "from_unit", "to_unit", "multiplier"]
