from django.views import generic


class FlexboxView(generic.TemplateView):
    template_name = "flexbox.html"


class FlexboxExamplesView(generic.TemplateView):
    template_name = "flexbox-examples.html"


class SemanticHTMLView(generic.TemplateView):
    template_name = "semantic.html"


class ResponsiveCSSView(generic.TemplateView):
    template_name = "responsive.html"
