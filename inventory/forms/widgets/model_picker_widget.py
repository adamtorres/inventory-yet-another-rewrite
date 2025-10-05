from django import forms


class ModelPickerWidget(forms.widgets.TextInput):
    template_name = "inventory/forms/widgets/model_picker_widget.html"
    placeholder = "needs a value"

    class Media:
        css = {
            'all': [
                'css/model_picker_widget.css',
            ]
        }
        js = [
            'js/search.js',
            'js/model_picker_widget.js',
        ]

    def __init__(self, attrs=None, *args, **kwargs):
        attrs = attrs or {}
        self.placeholder = kwargs.get("placeholder", self.placeholder)
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["placeholder"] = value or self.placeholder
        # TODO: Don't like using name.split("__prefix__-", 1)[1] to get the field name from within widget template.
        if "__prefix__" in name:
            context["widget"]["field_name"] = name.split("__prefix__-", 1)[1]
        else:
            context["widget"]["field_name"] = name
        return context
