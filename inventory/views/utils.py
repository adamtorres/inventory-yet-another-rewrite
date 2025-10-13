import json
import logging

import dateparser
from django.db import models

from rest_framework import response, views


logger = logging.getLogger(__name__)


class APISearchView(views.APIView):
    model = None
    serializer = None
    prefetch_fields = []
    select_related_fields = []
    search_terms = {}
    order_fields = []

    def build_search_filter(self, search_terms):
        """
        Builds the Q object to search self.model.objects.

        :param search_terms: dict with term as key and search values as a list.  Keys might have prefixes.
        :return: a pair of Q objects to apply to self.model.objects. (include Q, exclude Q)
        """
        # Full query string: |name=fuji&|name=gala&|name=red+delicious&name=apple&-name=juice&|unit=113&|unit=80&-unit=#10

        # Full query string split for legibility
        # |name=fuji
        # |name=gala
        # |name=red+delicious
        # name=apple
        # -name=juice
        # |unit=113
        # |unit=80
        # -unit=#10

        # Converted to lists by prefix/term
        # |name = ["fuji", "gala", "red delicious"]
        # name = ["apple"]
        # -name = ["juice"]
        # |unit = ["113", "80"]
        # -unit = ["#10"]
        exact_match_fields = ["id", "order_number"]
        q_dict = {}
        for search_term, value_list in search_terms.items():
            if not value_list:
                continue
            if search_term.startswith("-") or search_term.startswith("|"):
                st_key = search_term[1:]
                and_or_ex = search_term[0]
            else:
                st_key = search_term
                and_or_ex = "&"
            if st_key not in q_dict:
                q_dict[st_key] = {"&": models.Q(), "|": models.Q(), "-": models.Q()}

            for value in value_list:
                one_value_q = models.Q()
                for field_name in self.search_terms[st_key]:
                    if field_name in exact_match_fields or field_name.endswith("__id"):
                        modifier = "__iexact"
                    else:
                        modifier = "__icontains"
                    pile_of_tokens = models.Q()
                    if st_key.endswith("_date"):
                        date_value = dateparser.parse(value).date()
                        pile_of_tokens &= models.Q(**{field_name + modifier: date_value})
                    else:
                        for token in value.strip().split(" "):
                            pile_of_tokens &= models.Q(**{field_name + modifier: token})
                    one_value_q = one_value_q | pile_of_tokens
                match and_or_ex:
                    case "|": q_dict[st_key]["|"] |= one_value_q
                    case "&": q_dict[st_key]["&"] &= one_value_q
                    case "-": q_dict[st_key]["-"] &= one_value_q
        include_q = models.Q()
        exclude_q = models.Q()
        for search_term, st_q in q_dict.items():
            # TODO: skip if a Q is empty?  Doesn't seem to do anything to the generated SQL.
            include_q &= st_q["&"] & st_q["|"]
            exclude_q &= st_q["-"]
        return include_q, exclude_q

    def get_queryset(self):
        qs = self.model.objects.all()
        qs = self.select_related_qs(qs)
        qs = self.prefetch_qs(qs)
        return qs

    def get(self, request, format=None):
        # prefix = type of search. Assumed AND but "-" excludes and "|" ORs.
        # none = this included with the others
        # | = this or any of the other | values
        # - = this excluded from the others
        echo = json.loads(request.GET.get("echo", "{}") or "{}")
        search_terms = self.get_search_terms_from_request(request)
        all_obj_requested = request.GET.get("all_objects", "0") == "1"
        if not search_terms and not all_obj_requested:
            # TODO: Should this default to no results if no filters?
            return response.Response(self.serializer(self.get_queryset().none(), many=True).data)
        include_q, exclude_q = self.build_search_filter(search_terms)
        qs = self.get_queryset().filter(include_q).exclude(exclude_q)
        # "DISTINCT ON (fields)" is not supported by sqlite.  Workaround is to get the list of ids and filter the final
        # qs on that.
        qs_ids = qs.values("id").distinct()
        qs = self.get_queryset().filter(id__in=qs_ids)
        if self.order_fields:
            qs = qs.order_by(*self.order_fields)
        qs = self.limit_result(qs, request)
        data = self.serializer(qs, many=True).data
        data_packet = {
            "echo": echo,
            "data": data
        }
        return response.Response(data_packet)

    def get_search_terms_from_request(self, request):
        """
        Extracts the values to search for from the GET params using the keys in self.search_terms.
        Adds the prefixes "-" and "|" for exclusion and OR matches.
        :param request: The request object.
        :return: A dict with just the terms provided.  No empty lists.
        """
        search_terms = {}
        for st in self.search_terms.keys():
            for prefix in ["-", "", "|"]:
                prefixed_st = prefix + st
                value = request.GET.getlist(prefixed_st)
                if value:
                    search_terms[prefixed_st] = request.GET.getlist(prefixed_st)
        return search_terms

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
