import json

from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from inventory import models as inv_models


def get_specified_attrs(obj, attr_list: list=None):
    if not attr_list and isinstance(obj, inv_models.Item):
        attr_list = [
            "price_in_unit_value", "order_date", "per_unit_price", "subunit_size", "unit_size", "to_unit"
        ]
    values = {}
    for attr in attr_list:
        if hasattr(obj, attr):
            values[attr] = getattr(obj, attr)
    return values


def single_item(i):
    print(f"i = {i}")
    print(f"i!r = {i!r}")
    i.add_attrs_for_price_in_unit("g")
    print(json.dumps(get_specified_attrs(i), indent=2, default=str, sort_keys=True))
    print(json.dumps(i.latest_order(), indent=2, default=str, sort_keys=True))



def run():
    item_names = ["peanut butter", "all purpose flour", "pumpkin puree", "tapioca pudding cup"]
    with monkey_patch_cursordebugwrapper(print_sql=False, confprefix="SHELL_PLUS", print_sql_location=False):
        for i in inv_models.Item.objects.filter(name__in=item_names):
            single_item(i)
            # TODO: Trying to work through the pudding cup issue.  Seems like I need a recursive model for unit size.
            # It would need to automagically calculate the smallest unit size price.
            # pb http://localhost:8000/inventory/source_item/35401
            # tapioca http://localhost:8000/inventory/source_item/36162
            # pumpkin http://localhost:8000/inventory/source_item/35357
            # apf http://localhost:8000/inventory/source_item/36159

