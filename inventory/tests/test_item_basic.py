from django.test import TestCase

from inventory import models as inv_models


class TestItemBasic(TestCase):
    fixtures = ["category", "item"]

    def test_simple(self):
        obj = inv_models.Item.objects.get(name__istartswith="b")
        self.assertEqual(obj.name, "Butter")

    def test_count(self):
        self.assertEqual(inv_models.Item.objects.count(), 6)
