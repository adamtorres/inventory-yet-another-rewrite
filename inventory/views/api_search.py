import json
import logging

from rest_framework import response, views

from .. import models as inv_models, serializers as inv_serializers


logger = logging.getLogger(__name__)


class APISearchView(views.APIView):
    model = None
    serializer = None
    prefetch_fields = None
    select_related_fields = None

    def get_queryset(self):
        qs = self.model.objects.all()
        qs = self.select_related_qs(qs)
        qs = self.prefetch_qs(qs)
        return qs

    def get(self, request, format=None):
        # prefix = type of search.
        # & or none = this included with the others
        # | = this or any of the other | values
        # - = this excluded from the others
        criteria = [
            {"search_target": "name", "value": "apple"},
            {"search_target": "-name", "value": "juice"},
            {"search_target": "|name", "value": "fuji"},
            {"search_target": "|name", "value": "gala"},
            {"search_target": "|name", "value": "red"},
        ]
        # Take all the "|name" values and build an OR filter
        #    (name ILIKE "%fuji%") OR (name ILIKE "%gala%") OR (name ILIKE "%red%")
        # Run through the "&name", "name", and the above and build the ANDed filter
        # (name ILIKE "%apple%") AND ((name ILIKE "%fuji%") OR (name ILIKE "%gala%") OR (name ILIKE "%red%"))
        # Tack on the "-name" values as "AND NOT"
        # (name ILIKE "%apple%") AND (
        #     (name ILIKE "%fuji%") OR (name ILIKE "%gala%") OR (name ILIKE "%red%")
        # ) AND NOT (name ILIKE "%juice%")
        # Having only a single "|name" would be no different than "name" or "&name"
        terms = request.GET.get('terms')
        logger.debug(f"APISearchView.get: terms = {terms!r}")
        logger.debug(f"request.data: {request.data!r}")
        if not terms:
            return response.Response(self.serializer(self.get_queryset().none(), many=True).data)
        # search_filter = self.model.objects.build_search_filter(terms)
        qs = self.get_queryset()
        qs = self.limit_result(qs, request)
        data = self.serializer(qs, many=True).data
        return response.Response(data)

    def limit_result(self, qs, request):
        try:
            limit = request.GET.get('limit')
            limit = int(limit or "0")
            if limit and limit > 0:
                qs = qs[:limit]
        except ValueError:
            logger.error(f"APISearchView.limit_result: ValueError for {limit!r}.  Ignoring limit.")
        return qs

    def prefetch_qs(self, qs):
        # Does one query per model filtering on the ids needed.
        if self.prefetch_fields:
            return qs.prefetch_related(*self.prefetch_fields)
        return qs

    def select_related_qs(self, qs):
        # Does one query with joins to each table.  Could possibly multiple results unintentionally.
        if self.select_related_fields:
            return qs.select_related(*self.select_related_fields)
        return qs


class ItemSearch(APISearchView):
    model = inv_models.Item
    serializer = inv_serializers.ItemSerializer
    prefetch_fields = ['category']
    # select_related_fields = ['category']


class SourceItemSearch(APISearchView):
    model = inv_models.SourceItem
    serializer = inv_serializers.SourceItemSerializer
    prefetch_fields = ['source', 'item', 'item__category']
    # select_related_fields = ['source', 'item', 'item__category']
