import json
import pathlib

from . import base_command
from ... import models as inv_models


class Command(base_command.MyBaseCommand):
    import_folder = None
    cache_category = {}
    cache_item = {}
    cache_source = {}
    cache_unit_size = {}

    def actual_handle(self, *args, **options):
        self.import_folder = pathlib.Path(options["import_folder"])
        self.populate_caches()
        # self.show_all_json_files()
        self.import_source()
        self.import_category()
        self.import_item()
        self.import_unit_size()
        self.import_source_item()

    def add_arguments(self, parser):
        parser.add_argument(
            '-i',
            '--import-folder',
            action='store',
            dest='import_folder',
            help="Location of the JSON files to import",
            required=True
        )

    def add_new_category(self, category_name):
        obj, _ = inv_models.Category.objects.get_or_create(name=category_name)
        self.cache_category[category_name] = obj
        return obj

    @staticmethod
    def clean_unit_size(raw_unit_size):
        remove_chars = "0123456789. -/"
        new_unit_size = raw_unit_size
        for rc in remove_chars:
            new_unit_size = new_unit_size.replace(rc, "")
        if new_unit_size == '"':
            new_unit_size = "in"
        if new_unit_size == "-#":
            # doesn't get here because "-" is in remove_chars
            new_unit_size = "#avg"
        if new_unit_size == "#":
            new_unit_size = "lb"
        if new_unit_size.startswith("#"):
            new_unit_size = "lb " + new_unit_size[1:]
        return new_unit_size

    def dummy_function(self):
        num_sources = inv_models.Source.objects.count()
        print(f"There {"is" if num_sources == 1 else "are"} {num_sources} Source{"" if num_sources == 1 else "s"}.")

    def get_category(self, category):
        if category not in self.cache_category:
            obj = self.add_new_category(category)
        else:
            obj = self.cache_category[category]
        return obj

    def get_item(self, item_name):
        tmp = self.cache_item.get(item_name.lower().strip())
        if not tmp:
            print(f"!! {item_name!r} not found when looking for {item_name.lower().strip()!r}.")
        return tmp

    def get_source(self, source_name):
        tmp = self.cache_source.get(source_name.lower().strip())
        if not tmp:
            print(f"!! {source_name!r} not found when looking for {source_name.lower().strip()!r}.")
        return tmp

    def get_unit_size(self, unit_size):
        tmp = self.cache_unit_size.get(unit_size.lower().strip())
        if not tmp:
            print(f"!! {unit_size!r} not found when looking for {unit_size.lower().strip()!r}.")
        return tmp

    def import_category(self):
        category_json_file = self.import_folder / "category.json"
        category_data = json.load(category_json_file.open("r"))
        for category in category_data:
            obj, created = inv_models.Category.objects.get_or_create(name=category)
            print(f"Category({obj.id}) {"was" if created else "was not"} created. {obj.name!r}")
            self.cache_category[obj.name] = obj

    def import_item(self):
        for item_json_file in self.import_folder.glob("items_for_*.json"):
            self.import_item_json_file(item_json_file)

    def import_item_json_file(self, item_json_file):
        item_data = json.load(item_json_file.open("r"))
        category_name = (item_data["group_name"] or "").lower()
        category = self.get_category(category_name)
        created_count = 0
        untouched_count = 0
        for item_name in item_data["full_list"]:
            # TODO: Is it worth making this faster?  This should only be done a handful of times.
            obj, created = inv_models.Item.objects.get_or_create(name=item_name.lower().strip(), category=category)
            created_count += 1 if created else 0
            if not created:
                untouched_count += 1
            self.cache_item[item_name.lower().strip()] = obj
        print(f"{category_name}: created({created_count}) untouched({untouched_count}) total({item_data["length"]})")

    def import_source(self):
        source_json_file = self.import_folder / "source.json"
        source_data = json.load(source_json_file.open("r"))
        consolidated_sources = {}
        for source in source_data:
            source["name"] = source["name"].lower().strip()
            if source["name"] not in consolidated_sources:
                consolidated_sources[source["name"]] = set()
            consolidated_sources[source["name"]].add(source["customer_number"])

        for source in consolidated_sources.keys():
            consolidated_sources[source] = list(consolidated_sources[source])
            consolidated_sources[source].sort()
            obj, created = inv_models.Source.objects.get_or_create(name=source)
            if obj.customer_number:
                tmp = list(set(obj.customer_number).union(consolidated_sources[source]))
                tmp.sort()
                if tmp != obj.customer_number:
                    # print(f"\tupdated customer_numbers from {obj.customer_number!r} to {tmp!r}")
                    obj.customer_number = tmp
                    obj.save()
            else:
                obj.customer_number = consolidated_sources[source]
                obj.save()
            print(f"Source({obj.id}) {"was" if created else "was not"} created. {obj.name!r}: {obj.customer_number!r}")
            self.cache_source[obj.name] = obj

    def import_source_item(self):
        # source, category, unit_size, subunit_size
        for source_item_json_file in self.import_folder.glob("source_items_by_source_*.json"):
            self.import_source_item_json_file(source_item_json_file)

    def import_source_item_json_file(self, source_item_json_file):
        si_data = json.load(source_item_json_file.open("r"))
        source = self.get_source(si_data["group_name"])
        print(f"{si_data["group_name"]}({source.id}) has {si_data["length"]} items")
        batch = []
        for i, si in enumerate(si_data["full_list"]):
            self.get_category(si["source_category"])
            unit_amount_text, unit_size = self.split_unit_size(si["unit_size"])
            batch.append(inv_models.SourceItem(
                source=source,
                item=self.get_item(si["common_name"]),
                brand="?",
                source_category=si["source_category"],
                quantity=si["pack_quantity"],
                unit_amount=si["unit_quantity"],
                unit_amount_text=unit_amount_text,
                unit_size=self.get_unit_size(self.clean_unit_size(si["unit_size"])),
                cryptic_name=si["cryptic_name"],
                expanded_name=si["verbose_name"],
                item_number=si["item_code"],
                extra_number=si["extra_code"],
            ))
            if (i % 50) == 0:
                inv_models.SourceItem.objects.bulk_create(batch)
                batch[:] = []
        if batch:
            inv_models.SourceItem.objects.bulk_create(batch)
            batch[:] = []
        si_count = inv_models.SourceItem.objects.filter(source__name=si_data["group_name"]).count()
        print(f"{si_data["group_name"]} now has {si_count} SourceItems.")

    def import_unit_size(self):
        unit_size_json_file = self.import_folder / "unit_size.json"
        unit_size_data = json.load(unit_size_json_file.open("r"))
        created_count = 0
        total_count = 0
        for unit in unit_size_data:
            obj, created = inv_models.UnitSize.objects.get_or_create(unit=unit)
            self.cache_unit_size[obj.unit] = obj
            created_count += 1 if created else 0
            total_count += 1
        print(f"UnitSize: created({created_count}) total({total_count})")

    def populate_caches(self):
        self.cache_source.update({obj.name: obj for obj in inv_models.Source.objects.all()})
        print(f"Cached {len(self.cache_source)} Source.")
        self.cache_category.update({obj.name: obj for obj in inv_models.Category.objects.all()})
        print(f"Cached {len(self.cache_category)} Category.")
        self.cache_unit_size.update({obj.unit: obj for obj in inv_models.UnitSize.objects.all()})
        print(f"Cached {len(self.cache_unit_size)} UnitSize.")
        self.cache_item.update({obj.name: obj for obj in inv_models.Item.objects.all()})
        print(f"Cached {len(self.cache_item)} Item.")

    def show_all_json_files(self):
        print(f"Searching for JSON files in {self.import_folder}...")
        found_folders = list(self.import_folder.glob("*.json"))
        found_folders.sort()
        for f in found_folders:
            print(f"\t{f}")

    @staticmethod
    def split_unit_size(raw_unit_size):
        """
        takes "15.5oz" and returns ["15.5", "oz"]
        takes "8-12#avg" and returns ["8-12", "lb avg"]
        takes "14#avg" and returns ["14", "lb avg"]

        :param raw_unit_size:
        :return:
        """
        remove_chars = "0123456789. -/"
        amount_text = ""
        for c in raw_unit_size:
            if c not in remove_chars:
                break
            amount_text += c
        unit_size = raw_unit_size[len(amount_text):]
        if raw_unit_size:
            print(f"{raw_unit_size!r} = {amount_text!r}, {unit_size!r}")
        return amount_text, unit_size
