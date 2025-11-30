# Project Log
## Repository

If the repo loses its remote, try this:

```shell
git remote add origin git@github.com:adamtorres/inventory-yet-another-rewrite.git
```

This happened when I tried out the portable version of [Gitnuro](https://gitnuro.com/) via:

```shell
~/apps/android-studio/jbr/bin/java -jar Gitnuro-linux-x86_64-1.5.0.jar
```

## Creation

### Environment
Using `pyenv` to check the latest version of base python and create a virtual environment.  In actuality, I forgot to do the update so the actual latest version at the time of execution was 3.13.4.

```
pyenv update
pyenv install --list | grep -e " [34]\.[123][0-9]"
pyenv virtualenv --copies 3.13.2 practice-inventory
```

### Create the project

Used the "New Project" dialog in PyCharm 2025.1.1.1 with the following settings/values.

* Location: ~/PycharmProjects/practice-inventory
* Interpreter type: Custom environment
* Environment: Select existing
* Type: Python
* Python path: ~/.pyenv/versions/practice-inventory/bin/python3
* Template Language: Django
* Template Folder: templates
* Application name: inventory
* Project name: practice_inventory
* Enable Django admin: checked

This created a folder in the `PycharmProjects` folder named `practice-inventory` with the following layout.

```
~/PycharmProjects/practice-inventory
  manage.py
  inventory
    migrations
      (effectively empty)
    admin.py, apps.py, models.py, tests.py, views.py
  practice_inventory
    asgi.py, settings.py, urls.py, wsgi.py
  templates
    (empty)
```

### Upgrade the environment

```
cd ~/PycharmProjects/practice-inventory
pyenv local practice-inventory
```

Check the current version of pip and see what PyCharm installed by default.
```
$ python -m pip list
Package  Version
-------- -------
asgiref  3.8.1
Django   5.2.2
pip      24.3.1
sqlparse 0.5.3
```

Upgrade pip.
```
python -m pip install pip --upgrade
```

### Create the git repo

Used PyCharm's menu `VCS` -> `Create Git repo` to start a new repository in the root folder.
Copied a `.gitignore` from a previous PyCharm project to get started.  This is a customized version which ignores
additional folders and files like `.python-version` and `.idea`.

Performed the first commit with the customary "Initial commit" message.

### Setting up Django Admin

Run the django admin command to create a superuser.  Need to include the environment variable as it complains about
being improperly configured.
```
$ django-admin check
Note that only Django core commands are listed as settings are not properly configured (error: Requested setting
INSTALLED_APPS, but settings are not configured. You must either define the environment variable DJANGO_SETTINGS_MODULE
or call settings.configure() before accessing settings.).
```

Trying a variety of ways to get `django-admin` to work.
```
$ DJANGO_SETTINGS_MODULE=practice_inventory.settings django-admin check

$ export DJANGO_SETTINGS_MODULE=practice_inventory.settings
$ django-admin check

$ django-admin check --settings practice_inventory.settings
```
Also tried these methods in another application which is already set up and working.  Got the same error.
Copy/pasted the folder and file names just in case some look-a-like character was used.

Then I found the `createsuperuser` command in the `manage.py` listing so I didn't have to use `django-admin`.
Then I also found that the migrations need to be run for there to be a table to hold the superuser information.

```
$ ./manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
... snip ...
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
```

Creating a user with a very basic password as this is just a practice app and I don't want to remember a 20 character
mess.
```shell
$ ./manage.py createsuperuser --username adam --email adam@example.com --skip-checks
```
The output of the `createsuperuser` command with user input.
```
Password: 
Password (again): 
This password is too short. It must contain at least 8 characters.
This password is too common.
Bypass password validation and create user anyway? [y/N]: y
Superuser created successfully.
```

Start the server and verify the superuser can log in.

```
./manage.py runserver
```

Go to `http://localhost:8000/admin` and log in.

## Inventory Application

### Initial customization

The default project layout uses a single file for models, views, and tests.  I tend to favor a folder for each so
individual models, views, and tests can be in their own files.

* Remove the individual files for `models.py`, `views.py`, and `tests.py`
* Create folders with the names, `models`, `views`, and `tests`
* Drop an empty `__init__.py` into each of those folders.
  * Using PyCharm's right-click menu `New` -> `Python Package` will automatically create the `__init__.py` files.

### Models

Source - where the products are purchased
  * Name
  * Active - on/off for if this source should appear in option lists like 'new order' or such.
  * customer number - usually only one customer number per source but if we track Costco members, there'd be more.
  * ~~contact~~ - details for the customer service contact - name/email/phone
    * Do we care about the history?  Should there be a separate table holding contact info so the most recent is current
      but we maintain the previous contacts?
    * Not currently on the model at this time

Category - simple object to limit choices for category names.
  * name - is a description for a name field truly necessary?
  * ingredient - yes/no for if this category is food or not.  Intended to be used to limit choices when adding items to 
    a recipe.

Item - Generic item - not associated with any specific source or brand
  * name - a generic non-branded name
  * Source Item Search - Ties Source Item to Item by search criteria.
    * A json object which can handle multiple distinct criteria.
      * "fuji apple", "gala apple", "red delicious apple"
      * Exclusions: "chocolate milk" but exclude "milk chocolate chip"
    * This search would be used to offer suggestions for products on a newly-created order.
      * Possibly do the searches after the order is created on a follow-up page.
      * Limit searches to line items which don't already have a set item.
    * Used as a backup for when new Source Items are added so we don't end up with "Beef Brisket", "Brisket", "Sugar", "Granulated Sugar", "White Sugar"
  * description - general description of the item
  * Category - This is our category.  We could have a "cheese" category instead of lumping it into "dairy".
    * This is a discrete model to help prevent typos

UnitSize - defines the size of the SourceItem.  Also used as subunit - packs within a container.
  * unit - the type of unit.  floz, pound, count, etc
    * Decided to move the amount of unit to the SourceItem.
    * This being its own model makes it more difficult to duplicate or typo

Source Item - the products purchased from the source
  * Source - Link to the source of this item
  * Item - Link to generic item
  * brand - text label to store the brand name.  Not too important.
  * source category - each supplier puts items in odd places.  This is plain text and not a discrete model.
  * unit amount - decimal defining how much of unit_size there is.
  * unit amount text - for when the unit amount is not a simple number like "9-12#avg"?
  * unit size - Uses UnitSize for this.  This just defines the unit of measure but not how much of it there is.
  * subunit size - For when there are packs of a thing.  "unit size" could be "8 subunit" and subunit would be "3 oz" for a box with 8 packs of pudding cups.
  * active - is this item still available at the unit/subunit size?
    * Individual size options might be discontinued if a brand changes how they do things.  We'd need to preserve the old but not allow new orders.
    * Is it worth it to have a date when the item was discontinued?
  * quantity - how many of the unit or subunit are there?
  * allow split pack - split pack is when something comes in a 6pk but we can get a single.  Usually at a higher price.
  * cryptic name - the name as it appears on the invoice.  Most places horribly abbreviate names
  * expanded name - the cryptic name but with all abbreviations spelled out.  Any unknown abbreviations are left as-is until known.
  * common name - the name we tend to use for the product.  We'd say "whipped cream" even if the item is "whipped topping".
  * source-specific item code(s) - most vendors have one code.  Some have two.

Order - order-level details for a specific order from a source
  * date delivered - I sometimes know when an order is placed but not always.
  * purchase order text - some random text assigned to a specific order.  Not used anymore

Order Line Item - items on the order
  * Order - the link to the order-level information
  * Source Item - created at time of order if one doesn't exist
  * Quantity ordered
  * Quantity delivered - might have some on back order
  * Remote stock - will be delivered later by fedex/ups/usps.  Not backorder.  Tiny difference.
  * expect backorder delivery - Sysco will sometimes be out of something we ordered but send a substitute.  In that 
    case, we will not get the originally ordered item.
  * prices - extended, pack, $/lb, tax, etc
  * weights - some vendors include individual weights.  Some don't.

### Test data

This assumes there is no data in the database for the inventory app.  Fixtures will be created from data created by
these instructions for use in tests.  If there is preexisting data, some tests will fail.  Also, if there is preexisting
data, it won't be there for long as some steps here will delete all data in the tables.

From the root of the project folder, create a `fixtures` folder within the `inventory` folder.

```shell
mkdir inventory/fixtures
```

Use a one-liner to create a pile of Category objects to use in tests.  These will be removed later and only exist in a
fixture.  The `inv_models` module is loaded via settings so we don't have to manually do the import every time.

```shell
./manage.py shell_plus -c  '[inv_models.Category.objects.create(name=n) for n in ["Dairy", "Beef", "Pork", "Chicken", "Drink", "Flavor", "Fruit", "Veggie", "Sauce", "Dessert", "Dry"]]'
```

Dump the test data to a json file.

```shell
./manage.py dumpdata --indent 2 --output inventory/fixtures/category.json inventory.category
```

Clean up the test data.

```
./manage.py shell_plus -c  'inv_models.Category.objects.all().delete()'
```

Same process for Source.  The create line is using double quotes as "Broulim's" has a single quote and there didn't
appear to be an easy way to escape single quotes within a single quoted string.

```
./manage.py shell_plus -c  "[inv_models.Source.objects.create(name=n) for n in [\"Sysco\", \"USFoods\", \"Shamrock\", \"Broulim's\", \"Costco\", \"Family Dollar\", \"Donated\", \"Whole Foods\", \"RSM\", \"Walmart\"]]"
./manage.py dumpdata --indent 2 --output inventory/fixtures/source.json inventory.source
./manage.py shell_plus -c  'inv_models.Source.objects.all().delete()'
```

And once again with the process for UnitSize but this time via shell_plus.
```shell
./manage.py shell_plus
```

Left out the preceding `>>>` to make copy/paste easier.

```python
from inventory import models as inv_models
inv_models.UnitSize.objects.create(unit="#10 can")
inv_models.UnitSize.objects.create(unit="floz")
inv_models.UnitSize.objects.create(unit="gallon")
inv_models.UnitSize.objects.create(unit="pound")
inv_models.UnitSize.objects.create(unit="oz")
inv_models.UnitSize.objects.create(unit="ct")
inv_models.UnitSize.objects.create(unit="dz")
```

And dumping the data is the same as for previous models.

```shell
./manage.py dumpdata --indent 2 --output inventory/fixtures/unitsize.json inventory.unitsize
```

Manually load the test data into the database.  This is useful for building new test data objects which depend on other
objects.

```
./manage.py loaddata --app inventory category source unitsize
```

Creating Item objects is a little more involved since they need the Category instance.

```
>>> dairy = Category.objects.get(name="Dairy")
>>> dry = Category.objects.get(name="Dry")
>>> inv_models.Item.objects.create(name="Butter", source_item_search_criteria="", description="Brick of butter", category=dairy)
>>> inv_models.Item.objects.create(name="Eggs", source_item_search_criteria="", description="Why are eggs included in dairy?", category=dairy)
>>> inv_models.Item.objects.create(name="All Purpose Flour", source_item_search_criteria="", description="Bag of flour", category=dry)
>>> inv_models.Item.objects.create(name="Sugar (Granulated)", source_item_search_criteria="", description="Bag of sugar", category=dry)
>>> inv_models.Item.objects.create(name="Sugar (Powdered)", source_item_search_criteria="", description="Bag of powdered sugar", category=dry)
>>> inv_models.Item.objects.create(name="Sugar (Light Brown)", source_item_search_criteria="", description="Bag of light brown sugar", category=dry)
```

### Entering data

#### Entering an invoice/order

##### The order-level data

* Go to the 'Enter invoice' page.
* Find the source in the control.
  * If the source doesn't exist, should be able to open a popup to quickly add it.
* Enter the date, invoice/order numbers, and any other order-level data.

At this point, an Order object should be created and saved.

##### The line items

* Allow add/change/remove for line items on the order.

### Terminology

#### Quantity and Price

* pack: the item shown on the site.  It could be a pack of one like a bag of flour or it could contain multiple items 
    like a box of 27 individual milk cartons.  This means the `per_pack_price` is for the whole item or group of items.
* SourceItem.quantity: Answers the question, how many of SI.unit_size is contained in the pack?  For the box of milk
    cartons, OLI.quantity will be 27 since there are 27 8oz milk cartons in a single pack.
* SourceItem.unit_amount/unit_amount_text: unit_amount is a number and unit_amount_text is a free-form text field.
    For something with a range of sizes, unit_amount_text would be used to show the range as "8-12".  A mathematically
    usable value will be in unit_amount.  For "8-12", it would be "10".
* SourceItem.unit_size: Standardizes the unit types.  This is simply "lb", "g", "gal", etc.  The quantity of this size
    is stored in SI.unit_amount and/or SI.unit_amount_text.

##### Examples

Ordered 4x 50# bag of flour:

* SourceItem.quantity = 1
* SourceItem.unit_amount = 50
* SourceItem.unit_amount_text = ""  # Not needed since the value is an exact amount.
* SourceItem.unit_size.unit = "lb"
* SourceItem.subunit_amount = NULL
* SourceItem.subunit_amount_text = NULL
* SourceItem.subunit_size.unit = NULL
* OrderLineItem.quantity_delivered = 4
* OrderLineItem.per_pack_price = 14.00
* OrderLineItem.extended_price = 56.00 (OrderLineItem.per_pack_price(14.00) * OrderLineItem.quantity_delivered(4))
* OrderLineItem.per_weight_price = 0.25 (OrderLineItem.per_pack_price(14.00) / SourceItem.unit_amount(50))
  * This is possible because SI.unit_size is a weight type.
* OrderLineItem.total_weight = NULL <- Should this be 50 * 4?
* OrderLineItem.per_pack_weights = NULL  <- Should this be [50, 50, 50, 50]?
* per unit price: 14.00 (OrderLineItem.per_pack_price(14.00) / SI.quantity(1))

Ordered 4x 6pk #10 corn:

* SourceItem.quantity = 6
* SourceItem.unit_amount = 1  # A single #10 can.  Should this be the weight/volume/count?
* SourceItem.unit_amount_text = ""
* SourceItem.unit_size.unit = "#10"
* SourceItem.subunit_amount = NULL
* SourceItem.subunit_amount_text = NULL
* SourceItem.subunit_size.unit = NULL
* OrderLineItem.quantity_delivered = 4
* OrderLineItem.per_pack_price = 9.00
* OrderLineItem.extended_price = 36.00 (9.00 * 4)
* OrderLineItem.per_weight_price = NULL
  * This is not possible because SI.unit_size is NOT a weight type.
* OrderLineItem.total_weight = NULL
* OrderLineItem.per_pack_weights = NULL
* per unit price: 1.50 (OrderLineItem.per_pack_price(9.00) / SI.quantity(6))

# Ideas

## Dynamically add supporting items

When adding an invoice, it would be handy to be able to add a SourceItem, Item, or Category without having to reload the
page.  A possibility might be [Django Unicorn](https://www.django-unicorn.com/docs/)
