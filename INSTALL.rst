OpenAction installation guide
=============================

1. Clone open-action repository in a web-unaccessible folder::
    
    git clone https://github.com/openpolis/open-action /usr/local/open-action-work

2. Create a dedicated virtualenv::

    mkvirtualenv open-action

3. Update required submodules::

    git submodule update --init 

4. Install Askbot following the official guide http://askbot.org/doc/install.html

   - Install askbot by the provided script::

         cd CLONEDIR/submodules/askbot-devel
         python setup.py develop

     (If you get HTTP error, run this command twice)

   - Create the database (PostgreSQL)

     You can use the script placed in extras/wipe_postgres_sb.sh or run::

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
        python manage.py migrate askbot_extensions

     Don't mind errors appearing during the migrations, if they're something like::

        ... already exist ...
     They shouldn't be a problem.

     At this point you can test the installation by::

         python manage.py runserver

     Check that no errors are thrown

5. Install openaction requirements::

    pip install -r CLONEDIR/openaction/requirements.txt

6. Merge ``CLONEDIR/openaction/urls.py.dist`` with ``WEBDIR/urls.py``

7. Merge ``CLONEDIR/openaction/openaction_settings.py`` with ``WEBDIR/settings.py``::

    cat CLONEDIR/openaction/openaction_settings.py >> WEBDIR/settings.py

8. Integrate openaction project

   - by creating symlinks::

      for l in action base lib askbot_extensions oa_social_auth oa_notification external_resource organization friendship action_request users ajax_select
      do
         ln -s CLONEDIR/openaction/$i WEBDIR/$i
      done

   - or one by one::

      ln -s CLONEDIR/openaction/action/ WEBDIR/action
      ln -s CLONEDIR/openaction/base/ WEBDIR/base
      ln -s CLONEDIR/openaction/lib/ WEBDIR/lib
      ln -s CLONEDIR/openaction/askbot_extensions/ WEBDIR/askbot_extension
      ln -s CLONEDIR/openaction/oa_social_auth/ WEBDIR/oa_social_auth
      ln -s CLONEDIR/openaction/external_resource/ WEBDIR/external_resource
      ln -s CLONEDIR/openaction/oa_notification/ WEBDIR/oa_notification
      ln -s CLONEDIR/openaction/organization/ WEBDIR/organization
      ln -s CLONEDIR/openaction/friendship/ WEBDIR/friendship
      ln -s CLONEDIR/openaction/action_request/ WEBDIR/action_request
      ln -s CLONEDIR/openaction/users/ WEBDIR/users
      ln -s CLONEDIR/openaction/ajax_select/ WEBDIR/ajax_select

   - or with a ``WEBDIR/settings.py`` hack::

      settings.site.addsitedir( 'CLONEDIR/openaction' )

9. Resync the DB::

    python manage.py syncdb

10. Install and run redis cache server (for ajax selects) with ``redis-server``

Now Open Action is installed correcty.

If you want to deploy your installation, follow the guide in DEPLOY.rst

