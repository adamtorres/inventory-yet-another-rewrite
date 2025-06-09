# Project Log

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
```
$ ./manage.py createsuperuser --username adam --email adam@example.com --skip-checks
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
  * customer number - pretty sure we only have one customer number per source
  * contact - details for the customer service contact - name/email/phone

Source Item - the products purchased from the source
  * source-specific item code
  * pack/quantity options
    * split pack is when something comes in a 6pk but we can get a single.  Usually at a higher price.
    * Individual size options might be discontinued if a brand changes how they do things.  We'd need to preserve the old but not allow new orders.
    * Maybe have an active list and an inactive list.  These values would be copied to line items so moving a value wouldn't break anything.
  * discontinued - on/off for if this should appear in option lists.
    * Is it worth it to have a date when the item was discontinued?
  * Item - Link to generic item

Item - Generic item - not associated with any specific source or brand
  * Source Item Search - Ties Source Item to Item by search criteria.
    * A json object which can handle multiple distinct criteria.
      * "fuji apple", "gala apple", "red delicious apple"
      * Exclusions: "chocolate milk" but exclude "milk chocolate chip"
    * This search would be used to offer suggestions for products on a newly-created order.
      * Possibly do the searches after the order is created on a follow-up page.
      * Limit searches to line items which don't already have a set item.
    * Used as a backup for when new Source Items are added so we don't end up with "Beef Brisket", "Brisket", "Sugar", "Granulated Sugar", "White Sugar"
  * Category - split to a discrete model so we have consistency?
    * Or would it simple enough to have a set list of strings somewhere and not allow free-form entry?

Category - simple object to limit choices for category names.

Order - order-level details for a specific order from a source
  * date delivered - I sometimes know when an order is placed but not always.
  * purchase order text - some random text assigned to a specific order.  Not used anymore

Order Line Item - items on the order
  * Source Item - created at time of order if one doesn't exist
  * Quantity ordered
  * Quantity delivered - might have some on back order
  * Remote stock - will be delivered later by fedex/ups/usps
  * prices - extended, pack, $/lb, tax, etc
  * pack/unit sizes

### Test data

This assumes there is no data in the database for the inventory app.  Fixtures will be created from data created by
these instructions for use in tests.  If there is preexisting data, some tests will fail.  Also, if there is preexisting
data, it won't be there for long as some steps here will delete all data in the tables.

From the root of the project folder, create a `fixtures` folder within the `inventory` folder.

```
mkdir inventory/fixtures
```

Use a one-liner to create a pile of Category objects to use in tests.  These will be removed later and only exist in a
fixture.

```
./manage.py shell_plus -c  '[inv_models.Category.objects.create(name=n) for n in ["Dairy", "Beef", "Pork", "Chicken", "Drink", "Flavor", "Fruit", "Veggie", "Sauce", "Dessert", "Dry"]]'
```

Dump the test data to a json file.

```
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

Manually load the test data into the database.  This is useful for building new test data objects which depend on other
objects.

```
./manage.py loaddata --app inventory category source
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