from django import forms

from inventory import models as inv_models
from inventory.forms import widgets as inv_widgets


class SourceItemTestDropDownForm(forms.Form):
    # template_name_ div, p, table, ul, label "django/forms/___.html"
    # template_name_table = "inventory/forms/source_item_test_drop_down_form_table.html"
    search_wider = forms.CharField(widget=inv_widgets.ModelPickerWidget(attrs={"placeholder": "name or code"}))
