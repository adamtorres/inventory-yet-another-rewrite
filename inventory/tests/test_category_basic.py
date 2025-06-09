from django.test import TestCase

from inventory import models as inv_models


class TestCategoryBasic(TestCase):
    fixtures = ["category"]

    def test_simple(self):
        obj = inv_models.Category.objects.get(name__istartswith="v")
        self.assertEqual(obj.name, "Veggie")

    def test_count(self):
        self.assertEqual(inv_models.Category.objects.count(), 11)
