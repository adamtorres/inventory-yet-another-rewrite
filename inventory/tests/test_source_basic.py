from django.test import TestCase

from inventory import models as inv_models


class TestSourceBasic(TestCase):
    fixtures = ["source"]

    def test_simple(self):
        obj = inv_models.Source.objects.get(name__istartswith="b")
        self.assertEqual(obj.name, "Broulim's")

    def test_count(self):
        self.assertEqual(inv_models.Source.objects.count(), 10)
