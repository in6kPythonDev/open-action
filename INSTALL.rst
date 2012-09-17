
OpenAction installation guide
=============================

This installation guide assumes that you have alrady cloned the Openaction code
and that you will work into the virtualenv you are going to create.

0. Create virtualenv askbot-devel

1. Installn Askbot:
    1.1 Clone askbot code from git://github.com/ASKBOT/askbot-devel.git
    1.2 Follow Askbot develop (http://askbot.org/doc/index.html): 
        1.2.1 Installing Askbot --> Intend to customize the forum?
        1.2.2 Create database for Askbot --> PostgreSQL
        1.2.3 Initial Configuration of Askbot --> Installing Askbot as a new Django project (standalone app) 
        1.2.4 Initialization and upgrade of the database for Askbot

2. Install submodules 'askbot-devel' and 'django-notification-brosner' in Openaction:
    2.1 launch git submodule update --init from your Openaction root directory

3. Install django-social-auth (pip install django-social-auth)

4. Merge Openaction urls.py.dist with the Askbot urls.py

5. copy&past the content of the openaction_settings.py into the askbot settings.py file

6. Integrate openaction project (this project)

    2.1 Link (ln command) the 'action' app into the Askbot installation root directory
    2.2 Link the 'base' app into the Askbot installation root directory
    2.3 Link the 'lib' app into the Askbot installation root directory
    2.4 Link the 'askbot_extensions' app into the Askbot installation root directory
    2.5 Link the 'oa_social_auth' app into the Askbot installation root directory
    2.6 Link the 'external_resource' app into the Askbot installation root directory
    2.7 Link the 'connection' app (placed into django-notification-brosner submodule) into the Askbot installation root directory
