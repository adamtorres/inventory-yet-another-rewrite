
# Common to all (probably)
Add a `.env` file to your app's root folder.

Add `python-dotenv` to your `requirements.txt`.

Make sure to run `pip install -r requirements.txt`.

# Python Anywhere

[Python Anywhere](http://pythonanywhere.com) has a free plan but is quite limited.  For a web application, you have to
be careful about how many requests are made concurrently.  For the free plan, only one is allowed.  If you try to make
an API call from within a running request, the application will lock up.

## Environment Variables

The file that starts the web app is located at `/var/www/<your username>_pythonanywhere_com_wsgi.py`.

Below the setting of `project_home`, add the `import` and `load_dotenv` lines.

```python
# add your project directory to the sys.path
project_home = '/home/justsomerandom/inventory-yet-another-rewrite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

import dotenv
dotenv.load_dotenv(os.path.join(project_home, '.env'))

# set environment variable to tell django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'practice_inventory.settings'

```