from django import forms

from inventory import models as inv_models
from inventory.forms import widgets as inv_widgets


class OrderLineItemForm(forms.ModelForm):
    template_name_table = "inventory/forms/order_line_item_form_table.html"
    template_name_div = "inventory/forms/order_line_item_form_div.html"
    order = forms.ModelChoiceField(queryset=inv_models.Order.objects.all(), widget=forms.HiddenInput)
    source_item = forms.ModelChoiceField(queryset=inv_models.SourceItem.objects.all(), widget=inv_widgets.ModelPickerWidget)
    line_item_number = forms.IntegerField(widget=forms.HiddenInput)
    quantity_ordered = forms.IntegerField()
    quantity_delivered = forms.IntegerField()
    remote_stock = forms.BooleanField(required=False)
    expect_backorder_delivery = forms.BooleanField(required=False)
    per_pack_price = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    extended_price = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    tax = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    per_weight_price = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    per_pack_weights = forms.JSONField(required=False)
    total_weight = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    notes = forms.CharField(required=False)
    damaged = forms.BooleanField(required=False)
    rejected = forms.BooleanField(required=False)
    rejected_reason = forms.CharField(required=False)

    class Meta:
        model = inv_models.OrderLineItem
        fields = [
            "order", "source_item", "line_item_number", "quantity_ordered", "quantity_delivered", "remote_stock",
            "expect_backorder_delivery", "per_pack_price", "extended_price", "tax", "per_weight_price",
            "per_pack_weights", "total_weight", "notes", "damaged", "rejected", "rejected_reason",
        ]

    def __init__(self, *args, source_pk: int = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source_item'].widget.attrs["source_pk"] = source_pk

    # def clean_material_cost_per_pack(self):
    #     return self.cleaned_data['material_cost_per_pack'] or 0.0

    def save(self, commit=True):
        # use self.cleaned_data['quantity']
        # set self.instance.quantity
        return super().save(commit=commit)


OrderLineItemFormset = forms.inlineformset_factory(
    inv_models.Order, inv_models.OrderLineItem, OrderLineItemForm,
    extra=3, can_delete=True,
)
