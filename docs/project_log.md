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
python -m pip list
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