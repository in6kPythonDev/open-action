
OpenAction installation guide
=============================

0. Clone open-action repository in a no web-accessible folder
    
    git clone https://github.com/openpolis/open-action /usr/local/open-action-work

1. Create a dedicated virtualenv

    mkvirtualenv open-action

2. Update required submodules

    git submodule update --init 

3. Install Askbot following the official guide http://askbot.org/doc/install.html

    3.1 Install askbot by the provided script

        cd CLONEDIR/submodules/askbot-devel

        python setup.py develop

        (If you get HTTP error, run this command twice)

    3.2 Create the database (PostgreSQL)

        You can use the script placed in extras/wipe_postgres_sb.sh
        or run:

         su psql
         psql
         create role USERNAME with createdb login encrypted password 'PASSWORD'; 
         create database DBNAME with owner=USERNAME;
         grant all privileges on database DBNAME to USERNAME;
         \q  

    3.3 Configure ASKBOT. Run:
        
        askbot-setup    

        The wizard will ask you some information.
        
        Project folder: insert the path where you will deploy openaction (eg. /var/www/openaction)

        THIS IS NOT THE PATH WHERE YOU CLONED OPENACTION

        DB name, user name and password.

        DB domain: specify 'localhost', if you don't open-action will not connect to PostgreSQL

    3.4 Initialize the database

         python manage.py syncdb 
         python manage.py migrate askbot 
         python manage.py migrate django_authopenid
    
        At this point you can test the installation by:

         python manage.py runserver (check no error)  

4.  Install requirements

    pip install -r requirements.txt

5.  Merge CLONEDIR/submodules/askbot-devel/urls.py.dist with WEBDIR/urls.py

6.  Merge CLONEDIR/submodules/askbot-devel/openaction_settings.py with WEBDIR/settings.py

7. Integrate openaction project

     7.1 Link (ln command) the 'action' app into the 
         Askbot installation root directory
     
        ln -s CLONEDIR/openaction/action/ WEBDIR/action

     7.2 Link the 'base' app into the Askbot installation root directory
     
        ln -s CLONEDIR/openaction/base/ WEBDIR/base

     7.3 Link the 'lib' app into the Askbot installation root directory
     
        ln -s CLONEDIR/openaction/lib/ WEBDIR/lib

     7.4 Link the 'askbot_extensions' app into the 
         Askbot installation root directory
     
        ln -s CLONEDIR/openaction/askbot_extensions/ WEBDIR/askbot_extension

     7.5 Link the 'oa_social_auth' app into the 
         Askbot installation root directory
     
        ln -s CLONEDIR/openaction/oa_social_auth/ WEBDIR/oa_social_auth 


Now Open Action is installed correcty.

If you want to deploy your installation, follow the guide in DEPLOY.rst

