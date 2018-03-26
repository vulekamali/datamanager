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

Setup the database:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Deploying an update

Check out the latest master locally.

From your repo, run

```
git push dokku master
```

Development
-----------

* Put javascript into ``budgetportal/static/javascript/app.js``
* Put SCSS stylesheets into ``budgetportal/static/stylesheets/app.scss``
* Install new asset packs with Bower: ``bower install -Sp package-to-install``
* Get better debugging with ``python manage.py runserver_plus``

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
                              DISCOURSE_SSO_SECRET=...
git push dokku master
dokku run python manage.py migrate
dokku run python manage.py createsuperuser
```

Also use `dokku domains` to configure the hostnames that your app will serve.


License
-------

MIT License
