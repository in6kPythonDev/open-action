
OpenAction installation guide
=============================

0. Create virtualenv askbot-devel

1. Follow Askbot develop (http://askbot.org/doc/index.html)

2. Integrate openaction project (this project)

    2.1 Link the 'action' app into the Askbot installation
    2.2 Link the 'base' app into the Askbot installation
    2.3 Link the 'lib' app into the Askbot installation
    2.4 Link the 'askbot_extensions' app into the Askbot installation
    2.5 Link the 'oa_social_auth' app into the Askbot installation

3. Install django-social-auth (pip install django-social-auth)

4. Merge urls.py.dist with the Askbot urls

5. copy&past the content of the openaction_settings into the askbot settings file
