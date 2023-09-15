# https://gist.github.com/jaddison/4506070

# fail 'successfully' if either of these modules aren't installed
from gevent import monkey
from psycogreen.gevent import patch_psycopg

# setting this inside the 'try' ensures that we only 
# activate the gevent worker pool if we have gevent installed
worker_class = 'gevent'

# this ensures forked processes are patched with gevent/gevent-psycopg2
def do_post_fork(server, worker):
    monkey.patch_all()
    patch_psycopg()

    # you should see this text in your gunicorn logs if it was successful
    worker.log.info("Made Psycopg2 Green")

post_fork = do_post_fork