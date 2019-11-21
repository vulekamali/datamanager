vulekamali
==========

This is the source code for the South African National and Provincial Budget Portal.

In addition to providing user-friendly overviews of the national and provincial
budget data, this django app provides Single Sign-on (SSO) and support for
maintaining correct and consistent data for the various tools and services
around vulekamali.

This django app used to just coordinate and serve data, hence being called
`datamanager`, but now serves the actual website, so it will be renamed appropriately.

Code Structure vision
---------------------

### HTML, CSS, Javascript

We use a yarn (Node.js) and webpack-based build system for CSS and Javascript.

You can find frontend code in the following places:

- HTML (Django template language)
  - Page templates in `budgetportal/templates`
  - Includes in `assets/js/...html`
- Javascript (ES6)
  - The package for the main site has `package.json` in the root, and source files in `assets/js`
  - A package providing react views for certain pages in `packages/webapp`
- CSS (SCSS) in `assets/scss`

Most of the HTML has been migrated from Jekyll as simply and quickly as possible
and we're figuring out how best to structure it going forward. *Find a balance
between fitting in to the existing style and moving towards standard django
template best practises* for the time being.

When vulekamali was a jekyll site, there was an attempt to have a component-
oriented file structure so that the HTML (Liquid template language), SCSS, and
Javascript for a component were all in the same folder.

When migrating to Django, we have tried to keep this structure but split out
HTML (django template language) into the django template folder, SCSS in
`assets/scss` and Javascript in `assets/js` but ran into trouble with javascript
reading some HTML files. We decided to leave Django template include files in
`assets/js` for the time being and set that up as an additional template directory.

### Python code

We're moving towards the following code structure:

    +-------+
    | views |
    +-------+
      |   |
      |   V
      | +-----------+
      | | summaries |
      | +-----------+
      |    |   |   |
      |    |   |   |
      V    V   |   V
    +--------+ |  +----------+          +------+
    | models | |  | datasets |---HTTP-->| CKAN |
    +--------+ |  +----------+          +------+
               |
               V
          +--------------+          +--------------+
          | openspending |---HTTP-->| OpenSpending |
          +--------------+          +--------------+

A lot of summary code has been implemented as part of models but should now
start moving to summaries, and just call out to models and datasets as needed.


Setting up Development environment
-----------------------

### Install frontend dependencies

First time you clone this repo, and any time frontend dependencies might have changed

```
yarn
```

### Run JS and CSS incremental build for the assets managed by yarn (except webapp package)

This is an incremental build and will rebuild the root bundle until you Ctrl+C out of it.

```
yarn build:dev
```

When it's done with the initial build it just sits waiting to build changes looking
like this - it won't show anything when building subsequent changes unless there
are errors:

![yarn incremental build](docs/vulekamali-yarn-incremental-build.png)

### Build changes in webapp package.

In another shell, build the webapp package. This is not an incremental build and needs to be rebuilt for each change in this package.

```
yarn build:webapp
```

### Start development server

```
docker-compose up db
```

Setup the database - either by running migrations against a new database, or by
loading a dump from elsewhere:

If you're setting up a new database:

```
docker-compose run --rm app python manage.py migrate
docker-compose run --rm app python manage.py loaddata development-first-user
```

Then run the server

```
docker-compose up
```

Now you can login with initial the *development superuser*:

Username: `admin@localhost`
Password: `password`

A fixture is needed to set this up instead of `createsuperuser` because Django Allauth is configured to require verified email addresses.

If you want to reset the database and start fresh:

```
docker-compose down --volumes
```

And then:

```
docker-compose up
```


### Load data

Load an initial set of financial years, spheres and governments. You might need to add more recent ones manually in the admin interface.

You can download data from the production datamanager to use in your test environment as follows:

```bash
for year in 2016-17 2017-18 2018-19 2019-20; do curl https://vulekamali.gov.za/${year}/national/departments.csv > departments-national-${year}.csv; done
for year in 2016-17 2017-18 2018-19 2019-20; do curl https://vulekamali.gov.za/${year}/provincial/departments.csv > departments-provincial-${year}.csv; done
```

You can load this data into your environment with:

```bash
docker-compose run --rm app python manage.py loaddata years-spheres-governments \
                                                      video-language \
                                                      events \
                                                      provincial-infrastructure-projects \
                                                      homepage
for year in 2016-17 2017-18 2018-19 2019-20; do docker-compose run --rm app python manage.py load_departments ${year} national departments-national-${year}.csv; done
for year in 2016-17 2017-18 2018-19 2019-20; do docker-compose run --rm app python manage.py load_departments ${year} provincial departments-provincial-${year}.csv; done
```

Finally load the 2019-20 featured national infrastructure projects on the Infrastructure Project Parts admin page via the Import buton. Find the file to import at `budgetportal/fixtures/infrastructure-projects-2019-20.csv`.

------

Create and run database migrations with

```
docker-compose run --rm app python manage.py makemigrations

```

### Development best practises

* Always maintain or improve test coverage
* Follow the principles of the [test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html#TheTestPyramid)

#### Python/Django

* Get better debugging with ``python manage.py runserver_plus``
* Format your code using Black: `budgetportal manage.py discours --exclude budgetportal/bulk_upload.py`

#### React stuff (package.json and packages/webapp/package.json)

TBC

#### Classic django+bower stuff:

* Put javascript into ``budgetportal/static/javascript/app.js``
* Put SCSS stylesheets into ``budgetportal/static/stylesheets/app.scss``
* Install new asset packs with Bower: ``bower install -Sp package-to-install``

### Frontend development

#### Root NPM package

See package.json and webpack.config.js

#### packages/webapp NPM package

See [README.md](packages/webapp/README.md)

Specifically, it is set up so that development can happen both directly against the webapp, e.g.

```
cd packages/webapp
yarn start
```

or

```
cd packages/webapp
yarn start:storybook
```

Or as part of the django app where it gets embedded

```
yarn build:webapp
```

and reloading the django page.

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

Logout from ckan might not send you to the right URL to logout from this site. You can manually go to logout from this app at http://localhost:8000/accounts/logout/.

### Additional environment variables sometimes needing customisation for development

| Environment variable | Description |
| -------------------- | ------------|
| `DEBUG_CACHE`          | Enable the django app cache. Normally disabled by `DEBUG=True`, this enables it for development - see more in `settings.py`. |

Running tests
--------------

All tests

```
docker-compose run --rm test
```

Specific tests, e.g.

```
docker-compose run --rm test python manage.py test budgetportal.tests.test_bulk_upload.BulkUploadTestCase
```

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
                              CKAN_API_KEY=... \
                              DATABASE_URL=postgresql://... \
                              EMAIL_HOST_PASSWORD=... \
                              DISCOURSE_SSO_SECRET=... \
                              RECAPTCHA_PRIVATE_KEY=... \
                              SENTRY_DSN=https://5999094b0e214151bdfef41a5ad513c2@sentry.io/1730285
git push dokku master
dokku run budgetportal python manage.py migrate
dokku run budgetportal python manage.py createsuperuser
dokku ps:scale budgetportal worker=1
```

Also use `dokku domains` to configure the hostnames that your app will serve.

### Authentication

Apart from the superuser, additional users authenticate using either username+password or OAuth with social media accounts, e.g. Google and Facebook.

To enable this, we use [django-allauth](django-allauth) add social media account providers which provide verified email addresses in Django Admin's Social Accounts section.

For Google, set up an OAuth Client ID in [Google API Console](https://console.developers.google.com/apis/credentials?project=vulekamali)


Loading departments in bulk
---------------------------

The departments and their metadata are loaded using the Django Manage Command `load_departments`.

The command can be called to update the production database using

```bash
DATABASE_URL=postgresql://...produser...:...prodpasswd...@proddbhost/budgetportal python manage.py load_departments 2018-19 national departments.csv
```

where

- `2018-19` is the financial year slug
- `national` is the sphere slug
- `departments.csv` is a CSV file as follows:

Required columns:

 - `government` - government name
 - `department_name`
 - `vote_number`

Optional columns:

 - `is_vote_primary` - TRUE or FALSE
 - `intro`
 - `website_url`

 [Markdown syntax](https://daringfireball.net/projects/markdown/syntax#header) must be used for formatting `intro`. e.g. 2 line breaks will result in new paragraphs. Use headings like `## Vote purpose`

 e.g. for national

 | government | department_name | vote_number | is_vote_primary | intro | website_url |
 |------------|-----------------|-------------|-----------------|-------|-------------|
| South Africa | The Presidency | 1 | TRUE | ## Vote purpose <br/><br/>Facilitate a common programme towards the ... <br/></br> ## Mandate <br/><br/>To serve the president in the execution of his ... | http://www.thepresidency.gov.za/ |
| South Africa | Centre for Public Service Innovation | 10 | FALSE | ## Vote purpose <br/><br/>Facilitate the unearthing, development and practical ...  <br/></br> ## Mandate <br/><br/> The responsibility for public sector innovation is vested in the Minister of Public Service... | www.cpsi.co.za |

e.g. for provincial

 | government | department_name | vote_number | is_vote_primary | intro | website_url |
 |------------|-----------------|-------------|-----------------|-------|-------------|
| Eastern Cape | Health | 3 | TRUE | ## Vision<br/><br/>A quality health service to the people of the ... <br/></br> ## Mission<br/><br/>To provide and ensure accessible comprehensive integrated ... <br/><br/> ## Core functions and responsibilities<br/><br/>The strategic objectives are in line with the implementation | |


License
-------

MIT License
