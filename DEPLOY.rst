Deploy Open Action
====================

When Open Action is correcty installed and you get no errors when you 
run the django web server (python manage.py runserver) and visit 
http://127.0.0.1:8000/ASKBOT_URL/ (set in settings.py), 
you are ready to deploy your installation.

2 minutes' deploy with apache2 + mod_wsgi + virtualenv
------------------------------------------------------

1. extras/deploy/deploy_with_apache2_wsgi_venv.sh
2. answer questions
3. copy django_venv.wsgi in your web cgi executable folder
4. copy oa.apache2 in your virtualhost sites dir

A bit more detailed guide
-------------------------

We will only explain the most common situation: apache2 + mod_wsgi + virtualenv

0.  Add your openaction site in the apache2 configuration

    You can choose to create a new virtualdomain and run openaction on a 
    dedicated domain (eg. http://openaction.??) or add an entry in an existent
    virtualdomain to run openaction under a root web folder
    (eg. http://yoursite.com/openaction )

    In both case you have to insert in your apache configuration the following
    lines, replacing OA_DEPLOY_DIR with the web folder where Open Action is
    installed, and OA_WEB_DIR (must match ASKBOT_URL) 
    with the path you want to reach Open Action with the browser.

    # just / if you install openaction on a root domain
    WSGIScriptAlias /OA_WEB_DIR /YOUR_CGI_PATH/django_venv.wsgi
     
    #Alias /m/ /OA_DEPLOY_DIR/static/
    #Alias /upfiles/ /OA_DEPLOY_DIR/askbot/upfiles/
    
    <DirectoryMatch "/OA_DEPLOY_DIR/askbot/skins/([^/]+)/media">
       Order deny,allow
       Allow from all
    </DirectoryMatch>
    
    <Directory "/OA_DEPLOY_DIR/askbot/upfiles">
       Order deny,allow
       Allow from all
    </Directory>
    
    #must be a distinct name within your apache configuration
    WSGIDaemonProcess openaction
    WSGIProcessGroup openaction
    
    #make all admin stuff except media go through secure connection
    <LocationMatch "/admin(?!/media)">
      RewriteEngine on
      RewriteRule /admin(.*)$ https://yoursite.com/OA_WEB_DIR/admin$1 [L,R=301]
    </LocationMatch>


1.  Set up the wsgi launch script

    1.1 Copy extras/django_venv.wsgi.dist from the dir where you cloned openaction to the
        openaction deploy folder.

    1.2 Rename it django_venv.wsgi

    1.3 Edit that file and insert the needed parameters (read the comments)

Now Open Action is ready to run on your web server.

If you get a 500 error check Apache's error log for debugging. 

Note about mod_wsgi and virtualenv
----------------------------------

Problem could be related to mod_wsgi + virtualenv + your default interpreter, 
please follow WSGI documentation at
http://code.google.com/p/modwsgi/wiki/VirtualEnvironments

(if the interpreter of you virtualenv is different from system python interpreter, see the WSGIPythonHome directive)
