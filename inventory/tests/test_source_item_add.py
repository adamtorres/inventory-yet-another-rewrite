from django.test import TestCase

from inventory import models as inv_models


class TestSourceItemAdd(TestCase):
    fixtures = ["source", "category", "item", "unitsize"]

    def setUp(self):
        self.sysco = inv_models.Source.objects.get(name="Sysco")
        self.butter = inv_models.Item.objects.get(name="Butter")
        self.pound = inv_models.UnitSize.objects.get(unit="pound")

    def test_defaults(self):
        # defaults: active=True, allow_split_pack=True
        si = inv_models.SourceItem.objects.create(
            source=self.sysco, cryptic_name="the cryptic name", expanded_name="the expanded name",
            common_name="the common name", item=self.butter, brand="the brand", delivered_package_unit_size=self.pound,
            delivered_package_amount=1, source_category="the source category"
        )
        self.assertTrue(si.active)
        self.assertTrue(si.allow_split_pack)
