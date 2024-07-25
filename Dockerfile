FROM python:3.9-bullseye

ENV POETRY_VIRTUALENVS_CREATE false
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1
ENV NODE_ENV production
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE DontWarn

# from https://github.com/nikolaik/docker-python-nodejs/blob/main/Dockerfile
RUN set -ex; \
  echo "deb https://deb.nodesource.com/node_18.x bullseye main" > /etc/apt/sources.list.d/nodesource.list && \
  wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
  wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
  apt-get update && \
  apt-get upgrade -yqq && \
  apt-get install -yqq nodejs yarn && \
  # dependencies for building Python packages \
  apt-get install -y build-essential; \
  # psycopg2 dependencies \
  apt-get install -y libpq-dev; \
  # git for codecov file listing \
  apt-get install -y git; \
  # cleaning up unused files \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -U poetry==1.7.1
RUN poetry config virtualenvs.create false

RUN pip install --no-cache-dir --use-pep517 "django-allauth==0.50.0"

# Copy, then install requirements before copying rest for a requirements cache layer.
COPY pyproject.toml poetry.lock /tmp/
RUN set -ex; \
  cd /tmp; \
  poetry install

COPY . /app

ARG USER_ID=1001
ARG GROUP_ID=1001

RUN set -ex; \
  addgroup --gid $GROUP_ID --system containeruser; \
  adduser --system --uid $USER_ID --gid $GROUP_ID containeruser; \
  chown -R containeruser:containeruser /app

USER containeruser

WORKDIR /app

RUN set -ex; \
  NODE_ENV=development yarn --ignore-optional;

CMD /app/bin/start.sh
