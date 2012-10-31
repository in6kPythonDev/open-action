OpenAction installation guide
=============================

* Clone open-action repository in a web-unaccessible folder::
    
    git clone https://github.com/openpolis/open-action /usr/local/open-action-work

* Create a dedicated virtualenv::

    mkvirtualenv open-action

* Update required submodules::

    git submodule update --init 

* Install Askbot following the official guide http://askbot.org/doc/install.html

  - Install askbot by the provided script::

        cd CLONEDIR/submodules/askbot-devel
        python setup.py develop

    (If you get HTTP error, run this command twice)

  - Create the database (PostgreSQL)

    You can use the script placed in ``extras/wipe_postgres_sb.sh`` or run::

        su POSTGRES_USER
        psql
        create role USERNAME with createdb login encrypted password 'PASSWORD'; 
        create database DBNAME with owner=USERNAME;
        grant all privileges on database DBNAME to USERNAME;
        \q  

    The ``POSTGRES_USER`` variable can take different values according to the postgresql installation.
    Under debian-squeeze, ``POSTGRES_USER`` is 'postgres'

  - Configure ASKBOT. Run::
        
        askbot-setup

    The wizard will ask you some information.
        
    Project folder 
        insert the path where you will deploy openaction (eg. /var/www/openaction)
        THIS IS NOT THE PATH WHERE YOU CLONED OPENACTION

    DB name, user name and password
        insert the db name, the user and the password, as defined durin DB creation

    DB domain
        specify ``'localhost'`` o ``'127.0.0.1'``, if you want open-action connect to PostgreSQL


  - Install ``psycopg2`` python module, to talk to postgres::
        
        pip install psycopg2

  - Initialize the database::

        python manage.py syncdb 
        python manage.py migrate askbot 
        python manage.py migrate django_authopenid

    Don't mind errors appearing during the migrations, if they're something like::

        ... already exist ...
    They shouldn't be a problem.

    At this point you can test the installation by::

        python manage.py runserver

    Check that no errors are thrown

* Install openaction requirements::

    pip install -r CLONEDIR/openaction/requirements.txt

* Merge ``CLONEDIR/openaction/urls.py.dist`` with ``WEBDIR/urls.py``::

    cat CLONEDIR/openaction/urls.py.dist >> WEBDIR/urls.py

* Merge CLONEDIR/openaction/openaction_settings.py with WEBDIR/settings.py

* Integrate openaction project, by creating symlinks::

    for l in action base lib askbot_extensions oa_social_auth users action_request oa_notification external_resource organization 
    do 
        ln -s CLONEDIR/openaction/$i WEBDIR/$i
    done

* Resync the DB::

    python manage.py syncdb

Now Open Action is installed correcty.

If you want to deploy your installation, follow the guide in DEPLOY.rst

