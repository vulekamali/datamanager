vulekamali Data Manager
=============

This app provides Single Sign-on (SSO) and support for maintaining correct and consistent data for the vulekamali Budget Data Portal by the National Treasury of South Africa.

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

### Deploy to staging
It is important to commit your changes to staging prior to committing to deployment.

In order to commit to staging, you must push your local branch to the 
`dokku@treasury1.openup.org.za:budgetportal-staging` repository under the `master` branch.

#### Server permissions
You require sufficient permissions to push to the machine where the staging app is built.

As of this writing, the machine is located at `treasury1.openup.org.za`

Generate a local SSH public-private key and share the public key with the server administrator. The administrator must ensure that you
have access to push to that machine.

If you encounter a permission issue with ssh-agent, run the following:

`ssh-add`

#### Set up dokku-staging remote repository
First, you'll need to add a remote repository

`git remote add dokku-staging dokku@treasury1.openup.org.za:budgetportal-staging`

Make sure your local branch is up to date with your new changes, then push this branch to staging

`git push -f dokku-staging YOUR-BRANCH-NAME:master`

You should see output in your console from the server, indicating the status of the deployment.

Once this deployment is finished, you should be able to see the changes (YAML format) at `https://datamanager-staging.vulekamali.gov.za`

#### Static & templates
In order to view the changes as they would appear in production, with templating, a Travis CI build will need to be initiated
for static-budget-portal.

For instructions on how to do this, [please see here](https://google.com)


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

Logout from ckan might not send you to the right URL to logout from DataManager. You can manually go to logout from this app at http://localhost:8000/accounts/logout/.

### Additional environment variables somtimes needing customisation for development

| Environment variable | Description |
| -------------------- | ------------|
| `DEBUG_CACHE`          | Enable the django app cache. Normally disabled by `DEBUG=True`, this enables it for development - see more in `settings.py`. |


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
dokku ps:scale budgetportal worker=1
```

Also use `dokku domains` to configure the hostnames that your app will serve.

### Authentication

Apart from the superuser, additional users authenticate using either username+password or OAuth with social media accounts, e.g. Google and Facebook.

To enable this, we use [django-allauth](django-allauth) add social media account providers which provide verified email addresses in Django Admin's Social Accounts section.

For Google, set up an OAuth Client ID in [Google API Console](https://console.developers.google.com/apis/credentials?project=vulekamali)

Loading departments and their datasets
--------------------------------------

The departments and their metadata are loaded using Django Manage Commands. The input format they expect is defined in the source header.

License
-------

MIT License
