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

## Do stuff
