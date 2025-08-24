# Item Search API http://localhost:8000/inventory/api/item?name=butter&category=dairy
# [   { "id": 17843, "name": "butter", "description": "", "category": "dairy" },
#     { "id": 17845, "name": "buttermilk", "description": "", "category": "dairy" },
#     { "id": 17853, "name": "european style butter", "description": "", "category": "dairy" },
#     { "id": 17854, "name": "european style butter margarine", "description": "", "category": "dairy" },
#     { "id": 17858, "name": "individual butter cup", "description": "", "category": "dairy" },
#     { "id": 17879, "name": "unsalted butter", "description": "", "category": "dairy" }]

# Pricing and unit conversion
# http://localhost:8000/inventory/api/items/selected?item_category_unit=butter~dairy~tbsp&item_category_unit=egg~dairy~x&item_category_unit=pumpkin+puree~canned+%26+dry~cup&item_category_unit=all+purpose+flour~canned+%26+dry~cup&item_category_unit=granulated+sugar~canned+%26+dry~cup
# http://localhost:8000/inventory/api/items/selected
#   ?item_category_unit=butter~dairy~tbsp
#   &item_category_unit=egg~dairy~x
#   &item_category_unit=pumpkin+puree~canned+%26+dry~cup
#   &item_category_unit=all+purpose+flour~canned+%26+dry~cup
#   &item_category_unit=granulated+sugar~canned+%26+dry~cup
# {   "count": 5,
#     "next": null,
#     "previous": null,
#     "results": [
#         { "id": 17292, "name": "all purpose flour", "category": "canned & dry", "per_unit_price": 0.4548,
#           "unit_size": "lb", "subunit_size": null, "per_other_unit_price": 0.12993636, "other_unit": "cup" },
#         { "id": 17410, "name": "granulated sugar", "category": "canned & dry", "per_unit_price": 0.8142,
#           "unit_size": "lb", "subunit_size": null, "per_other_unit_price": 0.37664892, "other_unit": "cup" },
#         { "id": 17522, "name": "pumpkin puree", "category": "canned & dry", "per_unit_price": 11.348333333333333,
#           "unit_size": "#10 can", "subunit_size": null, "per_other_unit_price": 0.9453161666666666,
#           "other_unit": "cup" },
#         { "id": 17843, "name": "butter", "category": "dairy", "per_unit_price": 3.281388888888889, "unit_size": "lb",
#           "subunit_size": null, "per_other_unit_price": 0.10270747222222222, "other_unit": "tbsp" },
#         { "id": 17851, "name": "egg", "category": "dairy", "per_unit_price": 0.4311111111111111, "unit_size": "ct",
#           "subunit_size": null, "per_other_unit_price": 0, "other_unit": "x" } ] }