from django.db import models

from ... import models as inv_models
from . import base_command

class Command(base_command.MyBaseCommand):
    """
    ./manage.py merge_items -k "egg" -d "eggs" "large eggs"
    """
    category_separator = "|"
    safe = False

    def actual_handle(self, *args, **options):
        self.safe = options["safe"]
        # take all dupe_items' names and add to keep_item's description in a JSON form.
        keep_item, dupe_items = self.get_items(options["keep_item"], options["dupe_item"])

        self.show_keep_item(keep_item)
        self.show_dupe_items(dupe_items)
        dupe_item_details = self.get_dupe_item_details(dupe_items)
        self.append_dupe_item_details_to_keep_item(keep_item, dupe_item_details)
        source_items_to_update = self.get_source_items_to_update(dupe_items)
        if source_items_to_update:
            self.update_source_items(keep_item, source_items_to_update)
        self.delete_dupe_items(dupe_items)

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--safe',
            action='store_true',
            dest='safe',
            help="Safe mode.  Do a dry-run and don't make any changes to the database.",
            required=False,
            default=False,
        )
        parser.add_argument(
            '-k',
            '--keep-item',
            action='store',
            dest='keep_item',
            help="exact name of item to keep after merge.  If not specified, one of the dupe items will be picked.",
            required=False
        )
        parser.add_argument(
            "-d",
            '--dupe-item',
            action='store',
            dest='dupe_item',
            nargs='+',
            help="exact name(s) of item(s) to remove after merge",
            required=True,
        )

    def append_dupe_item_details_to_keep_item(self, keep_item, dupe_item_details):
        needs_saved = False
        if dupe_item_details["descriptions"]:
            keep_item.description += "\n" + ("\n".join(dupe_item_details["descriptions"]))
            needs_saved = True
        dupe_category_names = set()
        for category_name in dupe_item_details["categories"]:
            if keep_item.category.name != category_name:
                dupe_category_names.add(category_name)
        if dupe_category_names:
            keep_item.description += f"\nCategories not matching kept item: {", ".join(map(repr, dupe_category_names))}"
            needs_saved = True
        if needs_saved:
            if not self.safe:
                keep_item.save()
            else:
                print("[SAFE MODE] Not updating keep_item with details from dupe_items:")
                print("  " + keep_item.description.replace("\n", "\n  "))
        else:
            print("No details on dupe items needs copied to kept item.")

    def delete_dupe_items(self, dupe_items):
        dupe_item_ids = [i.id for i in dupe_items]
        count_of_items_to_delete = inv_models.Item.objects.filter(id__in=dupe_item_ids).count()
        if len(dupe_items) == count_of_items_to_delete:
            if not self.safe:
                inv_models.Item.objects.filter(id__in=dupe_item_ids).delete()
            else:
                not_deleted_count = inv_models.Item.objects.filter(id__in=dupe_item_ids).count()
                print(f"[SAFE MODE] Not deleting {not_deleted_count} Items.")
        else:
            print(f"Found {count_of_items_to_delete} when the dupe list has {len(dupe_items)}.")

    @staticmethod
    def get_dupe_item_details(dupe_items):
        details = {
            "descriptions": set(),
            "categories": set(),
        }
        for item in dupe_items:
            if item.description.strip():
                details["descriptions"].add(item.description.strip())
            details["categories"].add(item.category.name)
        return details

    def get_items(self, keep_item_name: str, dupe_item_names: list[str]):
        """
        Returns a keep_item if keep_item_name is specified and returns dupe_items.
        If keep_item_name is specified but not found, will print error and exit.
        If keep_item_name matches multiple Items, will print error and exit.
        If dupe_item_names matches no Items, will print error and exit.

        :param keep_item_name:
        :param dupe_item_names:
        :return:
        """
        keep_item = None
        if keep_item_name:
            filter_kwargs = self.item_name_to_filter_kwarg(keep_item_name)
            try:
                keep_item = inv_models.Item.objects.get(**filter_kwargs)
            except inv_models.Item.MultipleObjectsReturned:
                print(f"Found multiple Items when looking for {keep_item_name!r}.")
                for item in inv_models.Item.objects.filter(**filter_kwargs):
                    self.show_item(item)
                exit(1)
            except inv_models.Item.DoesNotExist:
                print(f"Could not find an Item with name {keep_item_name!r}.")
                exit(1)

        q = models.Q()
        for dupe_item_name in dupe_item_names:
            q |= models.Q(**self.item_name_to_filter_kwarg(dupe_item_name))
        dupe_items = inv_models.Item.objects.filter(q)
        if keep_item:
            dupe_items = dupe_items.exclude(id=keep_item.id)
        dupe_items = list(dupe_items)
        if not dupe_items:
            print(f"Could not find any Items with name(s) {dupe_item_names!r}")
            exit(1)
        if not keep_item:
            if len(dupe_items) > 1:
                # move a dupe_item to keep_item if no keep_item specified.
                keep_item = dupe_items.pop()
            elif len(dupe_items) == 1:
                print(f"Only one item found Item({dupe_items[0].id}) for {dupe_item_names}.  Nothing to merge it with.")
                exit(0)
        return keep_item, dupe_items

    @staticmethod
    def get_source_items_to_update(dupe_items):
        source_items_to_update = set()
        for dupe_item in dupe_items:
            source_items_to_update.update(dupe_item.sourceitem_set.all())
        return source_items_to_update

    def item_name_to_filter_kwarg(self, item_name):
        item_name, category_name = self.split_item_and_category_names(item_name)
        filter_kwargs = {"name": item_name}
        if category_name:
            filter_kwargs["category__name"] = category_name
        return filter_kwargs

    @staticmethod
    def show_item(item, prefix="", indent=0):
        print(f"{" " * indent}{prefix}{" " if prefix else ""}Item: {item.id} / {item.name!r} / {item.description} / {item.category.name!r}")
        for si in item.sourceitem_set.all():
            print(f"{" " * (indent+1)}↳ SourceItem({si.id}): {si}")

    def show_dupe_items(self, dupe_items):
        print("Duplicate items to remove:")
        for dupe_item in dupe_items:
            self.show_item(dupe_item, indent=2)

    def show_keep_item(self, keep_item):
        print("Keeping:")
        self.show_item(keep_item, indent=2)

    def split_item_and_category_names(self, item_and_category_name):
        if self.category_separator in item_and_category_name:
            return item_and_category_name.split(self.category_separator, 1)
        return item_and_category_name, None

    def update_source_items(self, keep_item, source_items_to_update):
        print(f"Updating SourceItems({[si.id for si in source_items_to_update]}) to point to Item({keep_item.id}).")
        for si in source_items_to_update:
            si.item = keep_item
        if not self.safe:
            inv_models.SourceItem.objects.bulk_update(source_items_to_update, ["item"])
        else:
            not_updated_count = inv_models.SourceItem.objects.filter(id__in=[si.id for si in source_items_to_update]).count()
            print(f"[SAFE MODE] Not updating {not_updated_count} SourceItems.")
