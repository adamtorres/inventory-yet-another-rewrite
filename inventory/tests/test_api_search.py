"""
/inventory/api/source_item_search?name=apple&|name=gala&|name=fuji&|name=red+delicious&-name=juice&|unit=113&|unit=80&-unit=%2310
{
    '-name': ['juice'],
    'name': ['apple'],
    '|name': ['gala', 'fuji', 'red delicious'],
    '-unit': ['#10'],
    '|unit': ['113', '80']
}

{
    'name': {
        '&': <Q: (OR: ('item__name__icontains', 'apple'), ('cryptic_name__icontains', 'apple'), ('expanded_name__icontains', 'apple'), ('common_name__icontains', 'apple'))>,
        '|': <Q: (OR: ('item__name__icontains', 'gala'), ('cryptic_name__icontains', 'gala'), ('expanded_name__icontains', 'gala'), ('common_name__icontains', 'gala'),
            ('item__name__icontains', 'fuji'), ('cryptic_name__icontains', 'fuji'), ('expanded_name__icontains', 'fuji'), ('common_name__icontains', 'fuji'),
            (AND: ('item__name__icontains', 'red'), ('item__name__icontains', 'delicious')), (AND: ('cryptic_name__icontains', 'red'), ('cryptic_name__icontains', 'delicious')), (AND: ('expanded_name__icontains', 'red'), ('expanded_name__icontains', 'delicious')), (AND: ('common_name__icontains', 'red'), ('common_name__icontains', 'delicious')))>,
        '-': <Q: (OR: ('item__name__icontains', 'juice'), ('cryptic_name__icontains', 'juice'), ('expanded_name__icontains', 'juice'), ('common_name__icontains', 'juice'))>
    },
    'unit': {
        '&': <Q: (AND: )>,
        '|': <Q: (OR: ('unit_size__amount__icontains', '113'), ('unit_size__unit__icontains', '113'), ('subunit_size__amount__icontains', '113'), ('subunit_size__unit__icontains', '113'),
            ('unit_size__amount__icontains', '80'), ('unit_size__unit__icontains', '80'), ('subunit_size__amount__icontains', '80'), ('subunit_size__unit__icontains', '80'))>,
        '-': <Q: (OR: ('unit_size__amount__icontains', '#10'), ('unit_size__unit__icontains', '#10'), ('subunit_size__amount__icontains', '#10'), ('subunit_size__unit__icontains', '#10'))>
    }
}
"""
from django import urls
from django.db import models
from django.test import RequestFactory, TestCase

from inventory import views as inv_views


class TestSourceItemSearch(TestCase):
    def setUp(self):
        self.url = urls.reverse("inventory:api_sourceitem_search")
        self.apple_search_terms = {
            '-name': ['juice'],
            'name': ['apple'],
            '|name': ['gala', 'fuji', 'red delicious'],
            '-unit': ['#10'],
            '|unit': ['80', '113']}
        qstr = "?name=apple&|name=gala&|name=fuji&|name=red+delicious&-name=juice&|unit=80&|unit=113&-unit=%2310"
        self.apple_request = RequestFactory().get(self.url + qstr)
        self.apple_view = inv_views.SourceItemSearch()
        self.apple_view.setup(self.apple_request)


    def test_get_search_terms_from_request(self):
        # Testing the search term dict built from the query string.
        # This is dependent on the order of list items.  If the query string in the request changes, this might break.
        search_terms = self.apple_view.get_search_terms_from_request(self.apple_request)
        self.assertEqual(self.apple_search_terms, search_terms)

    @staticmethod
    def q_up(field_names, values, operation):
        # Helper function to build the very repetitive models.Q objects.
        q = models.Q()
        for field_name in field_names:
            value_q = models.Q()
            for value in values.strip().split(" "):
                kwargs = {field_name + "__icontains": value}
                value_q &= models.Q(**kwargs)
            match operation:
                case "&": q &= value_q
                case "|": q |= value_q
        return q

    def test_build_search_filter(self):
        # Checking the Q objects returned that are built from the search term dict.
        include_q_objects, exclude_q_objects = self.apple_view.build_search_filter(self.apple_search_terms)
        name_field_names = ["item__name", "cryptic_name", "expanded_name", "common_name"]
        unit_field_names = ["unit_size__amount", "unit_size__unit", "subunit_size__amount", "subunit_size__unit"]

        # inclusions
        apple = self.q_up(name_field_names, "apple", "|")
        gala = self.q_up(name_field_names, "gala", "|")
        fuji = self.q_up(name_field_names, "fuji", "|")
        red_delicious = self.q_up(name_field_names, "red delicious", "|")
        unit_counts_eighty = self.q_up(unit_field_names, "80", "|")
        unit_counts_one_thirteen = self.q_up(unit_field_names, "113", "|")

        # exclusions
        juice = self.q_up(name_field_names, "juice", "|")
        unit_counts_number_ten_can = self.q_up(unit_field_names, "#10", "|")

        expected_q_objects = (apple & (gala | fuji | red_delicious))
        expected_q_objects &= unit_counts_eighty | unit_counts_one_thirteen

        expected_excluded_q_objects = models.Q()
        expected_excluded_q_objects &= juice
        expected_excluded_q_objects &= unit_counts_number_ten_can
        tests = [(expected_q_objects, include_q_objects), (expected_excluded_q_objects, exclude_q_objects)]
        for exp, act in tests:
            with self.subTest(expected=exp, actual=act):
                self.assertEqual(exp, act)

    # def test_sql(self):
    #     # Not testing the SQL as it looks like it would change depending on the specific backend.
    #     search_terms = self.apple_view.get_search_terms_from_request(self.apple_request)
    #     include_q, exclude_q = self.apple_view.build_search_filter(search_terms)
    #     qs = self.apple_view.get_queryset().filter(include_q).exclude(exclude_q)
    #
    #     with CaptureQueriesContext(connection) as ctx:
    #         list(qs)
    #         captured_sql = ctx.captured_queries[0]["sql"]
    #         print(f"{captured_sql}")
