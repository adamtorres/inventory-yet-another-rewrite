from django.views import generic

from .category import CategoryCreateView, CategoryDeleteView, CategoryDetailView, CategoryUpdateView, CategoryListView
from .item import ItemListView, ItemCreateView, ItemDetailView, ItemUpdateView, ItemDeleteView
from .tag import TagCreateView, TagListView, TagDeleteView, TagDetailView, TagUpdateView

class MarketHomepageView(generic.TemplateView):
    template_name = "market/homepage.html"
