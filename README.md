Budget Portal
=============

Setting up Development environment
-----------------------

Requires a recent Python 2.7 and Postgres 9 point release.

Install system dependencies for psycopg2. e.g. on Ubuntu:

```
sudo apt-get update
sudo apt-get install libpq-dev python-dev
```

Install python dependencies

```
virtualenv --no-site-packages env
source env/bin/activate
pip install -r requirements.txt
```

Add the dokku remote to you local clone

```
git remote add dokku@treasury1.openup.org.za:budgetportal
```

Setup the database - either by running migrations against a new database, or by
loading a dump from elsewhere:

If you're setting up a new database:

```
python manage.py migrate
python manage.py createsuperuser
```

Then run the server

```
python manage.py runserver_plus
```

### Deploying an update

Check out the latest master locally.

From your repo, run

```
git push dokku master
```

### Development

* Put javascript into ``budgetportal/static/javascript/app.js``
* Put SCSS stylesheets into ``budgetportal/static/stylesheets/app.scss``
* Install new asset packs with Bower: ``bower install -Sp package-to-install``
* Get better debugging with ``python manage.py runserver_plus``

### Single Sign-on (SSO)

To use the Single Sign-on functionality in local development, make sure you set the relevant environment variables to match your local setup, e.g.

```
HTTP_PROTOCOL=http \
DISCOURSE_SSO_SECRET=... \
CKAN_SSO_URL=http://localhost/user/login \
EMAIL_HOST=localhost \
EMAIL_PORT=2525 \
EMAIL_USE_TLS= \
python manage.py runserver
```

Logout from ckan might not send you to the right URL. You can manually go to logout from this app at http://localhost:8000/accounts/logout/.

Production deployment
---------------------

### Initial Deployment

You'll need:

* API key for a CKAN user who can modify datasets in the `national-treasury` organisation

Create and configure the app

```bash
dokku apps:create budgetportal
dokku config:set budgetportal DJANGO_DEBUG=false \
                              DISABLE_COLLECTSTATIC=1 \
                              DJANGO_SECRET_KEY=some-secret-key \
                              NEW_RELIC_APP_NAME=cool app name \
                              NEW_RELIC_LICENSE_KEY=new relic license key \
                              CKAN_API_KEY=... \
                              DATABASE_URL=postgresql://... \
                              EMAIL_HOST_PASSWORD=... \
                              DISCOURSE_SSO_SECRET=... \
                              RECAPTCHA_PRIVATE_KEY=...
git push dokku master
dokku run python manage.py migrate
dokku run python manage.py createsuperuser
```

Also use `dokku domains` to configure the hostnames that your app will serve.

Loading departments and their datasets
--------------------------------------

The departments, their metadata and their datasets are loaded using Django Manage Commands. The input format they expect is defined in the source header.

e.g. loading department dataset resource files locally:

```bash
python manage.py upload_department_datasets 2018-19 provincial ../data/provincial/from-jonathan/2018/budget-info/department-mapping.csv
```

and in production:

```bash
DATABASE_URL=postgresql://budgetportal:.../budgetportal CKAN_API_KEY=... python manage.py upload_department_datasets 2018-19 provincial ../data/provincial/from-jonathan/2018/budget-info/department-mapping.csv
```

These commands have built in help if you run them with just `--help` where you can see accepted arguments.

You can update resources uploaded previously with `--overwrite`

e.g.

```bash
python manage.py upload_department_datasets --overwrite 2018-19 provincial ../data/provincial/from-jonathan/2018/budget-info/department-mapping-fix-mp-xls.csv
```

License
-------

MIT License
