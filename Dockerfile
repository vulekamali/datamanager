FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY requirements-test.txt /code/
COPY tox.ini /code/
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install tox codecov
COPY . /code/

# PhantomJS
ENV PHANTOMJS_VERSION 2.1.1
RUN wget --no-check-certificate -q -O - https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 | tar xjC /opt
RUN ln -s /opt/phantomjs-$PHANTOMJS_VERSION-linux-x86_64/bin/phantomjs /usr/bin/phantomjs
