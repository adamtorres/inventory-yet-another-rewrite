import json

from django.db import models
from django.db.models import functions
import requests

from . import my_base_command
from ... import models as mkt_models


class Command(my_base_command.MyBaseCommand):
    remote_host = "http://localhost:9000"

    def actual_handle(self, *args, **options):
        self.process_items()
        # self.process_orders()

    @staticmethod
    def compare_to_existing(new_data: list, unique_fields: list, model, field_xlate: dict=None):
        create_these = []
        update_these = []
        for new_item in new_data:
            kwargs = {}
            for field in unique_fields:
                new_value = new_item[field]
                existing_field = field_xlate[field] if field_xlate else field
                if isinstance(new_value, str):
                    existing_field += "__iexact"
                kwargs[existing_field] = new_value
            qs = model.objects.filter(**kwargs)
            if not qs.exists():
                create_these.append(new_item)
                continue
            new_item["existing_ids"] = list(qs.values_list("id", flat=True).order_by("id"))
            update_these.append(new_item)
        return create_these, update_these

    def create_or_replace_categories(self, categories):
        lower_categories = [category.lower() for category in categories]
        existing_category_names = list(
            mkt_models.Category.objects.annotate(lower_name=functions.Lower("name")).filter(
                lower_name__in=lower_categories).values_list("lower_name", flat=True))
        objs_to_create = [
            mkt_models.Category(name=category.title())
            for category in lower_categories if category not in existing_category_names]
        mkt_models.Category.objects.bulk_create(objs_to_create, ignore_conflicts=True, unique_fields=["name"])
        return {c.name.lower(): c for c in mkt_models.Category.objects.all()}

    def create_items(self, items_to_create):
        # Note: Ignoring tags as that was a feature that wasn't used in the old system.  They are all empty.
        # Note: Making use of tags to hold the old Item.id to use for lookups when adding items to orders.
        categories = list(set([item["category"] for item in items_to_create]))
        categories.sort()
        all_categories = self.create_or_replace_categories(categories)
        item_id_tag_xlate = self.create_temporary_tags(items_to_create)
        created_items = []
        for item in items_to_create:
            obj = mkt_models.Item.objects.create(
                name=item["name"],
                category=all_categories[item["category"].lower()],
            )
            obj.tags.add(item_id_tag_xlate[item["id"]])
            created_items.append(obj)
        return len(created_items)

    def create_orders(self, orders_to_create):
        # TODO: Finish creating Order and OrderLineItem objects.
        for order in orders_to_create:
            # Create the order object.
            for line_item in order["line_items"]:
                # Lookup the item by uuid in the tags.
                pass

    @staticmethod
    def create_temporary_tags(list_of_things_with_ids, field_to_use="id", prefix=""):
        tag_xlate = {}
        for thing in list_of_things_with_ids:
            obj = mkt_models.Tag.objects.create(
                value=f"{prefix + ":" if prefix else ""}{field_to_use}={thing[field_to_use]}")
            tag_xlate[thing[field_to_use]] = obj
        return tag_xlate

    def get_data(self, url):
        response = requests.get(self.remote_host + url)
        return response.json()

    def get_item_data(self):
        url = "/market/api/items"
        data = self.get_data(url)
        return data

    def get_order_data(self):
        url = "/market/api/orders"
        data = self.get_data(url)
        return data

    def process_generic(self, model, name, unique_fields:list[str], field_xlate: dict=None):
        self.stdout.write(f"Getting {name}s from API...")
        new_yadda_data = getattr(self, f"get_{name}_data")()
        self.stdout.write(f"\tGot {len(new_yadda_data)} total {name}s.")
        create_yaddas, update_yaddas = self.compare_to_existing(new_yadda_data, unique_fields, model, field_xlate)
        self.stdout.write(f"\t\t{len(create_yaddas)} {name}s to create")
        self.stdout.write(f"\t\t{len(update_yaddas)} {name}s to update")
        create_result = getattr(self, f"create_{name}s")(create_yaddas)
        self.stdout.write(f"\tCreated {create_result} {name}s")

    def process_items(self):
        self.process_generic(mkt_models.Item, "item", ["name", "category"], {
            "name": "name",
            "category": "category__name",
        })

    def process_orders(self):
        self.process_generic(mkt_models.Order, "order", ["expected_date", "who", "contact_number"])
