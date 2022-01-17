NiceDB / NeoDB - Getting Start
==============================
This is a very basic guide with limited detail, contributions welcomed

Install
-------
Install PostgreSQL, Redis and Python if not yet

Setup database
```
CREATE DATABASE neodb ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE template0;
\c neodb;
CREATE EXTENSION hstore WITH SCHEMA public;
CREATE ROLE neodb with LOGIN ENCRYPTED PASSWORD 'abadface';
GRANT ALL ON DATABASE neodb TO neodb;
```

Create and edit your own configuration file (optional but very much recommended)
```
mkdir mysite && cp boofilsic/settings.py mysite/
export DJANGO_SETTINGS_MODULE=mysite.settings
```

Create and use `venv` as you normally would, then install packages 
```
python3 -m pip install -r requirements.txt
```

Quick check
```
python3 manage.py check
```

Initialize database
```
python3 manage.py makemigrations users books movies games music sync mastodon management collection
python3 manage.py migrate users
python3 manage.py migrate
```

Build static assets
```
python3 manage.py collectstatic
```


Start services
--------------
Make sure PostgreSQL and Redis are running

Start job queue server
```
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES  # required and only for macOS, otherwise it may crash
python3 manage.py rqworker --with-scheduler doufen export mastodon
```

Run web server in dev mode
```
python3 manage.py runserver 0.0.0.0:80
```

It should be ready to serve from here, to run web server for production, consider `gunicorn -w 8 boofilsic.wsgi` in systemd or sth similar


Migrate from an earlier version
-------------------------------
Update database
```
python3 manage.py makemigrations
python3 manage.py migrate
```

Rebuild static assets
```
python3 manage.py sass common/static/sass/boofilsic.sass common/static/css/boofilsic.min.css -t compressed
python3 manage.py sass common/static/sass/boofilsic.sass common/static/css/boofilsic.css
python3 manage.py collectstatic
```


Other maintenance tasks
-----------------------
Requeue failed jobs
```
rq requeue --all --queue doufen
```