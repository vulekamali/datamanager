Budget Portal
=============

Setting up Development environment
-----------------------

```
virtualenv --no-site-packages env
source env/bin/activate
pip install -r requirements.txt
```

Edit ``code4sa/settings.py`` and set some options

* ``GOOGLE_ANALYTICS_ID`` to the GA tracking code

Finally, setup the database:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Development
-----------

* Put javascript into ``code4sa/static/javascript/app.js``
* Put SCSS stylesheets into ``code4sa/static/stylesheets/app.scss``
* Install new asset packs with Bower: ``bower install -Sp package-to-install``
* Get better debugging with ``python manage.py runserver_plus``

Production deployment
---------------------

Production deployment assumes you're running on Heroku.

You will need:

* a django secret key
* a New Relic license key
* a cool app name

```bash
heroku create
heroku addons:add heroku-postgresql
heroku config:set DJANGO_DEBUG=false \
                  DISABLE_COLLECTSTATIC=1 \
                  DJANGO_SECRET_KEY=some-secret-key \
                  NEW_RELIC_APP_NAME=cool app name \
                  NEW_RELIC_LICENSE_KEY=new relic license key
git push heroku master
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

License
-------

MIT License
