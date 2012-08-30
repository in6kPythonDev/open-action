
OpenAction installation guide
=============================

0. Create virtualenv askbot-devel

1. Follow Askbot develop (http://askbot.org/doc/index.html)

2. Integrate openaction project (this project)

    2.1 Link the 'action' app into the Askbot installation
    2.2 Merge urls.py.dist with the Askbot urls
    2.3 Merge openaction_settings.py with the Askbot settings
    2.4 Add 'action' app to the Askbot installed apps (in Askbot settings)
    2.5 Link the 'base' app into the Askbot installation
    2.6 Link the 'lib' app into the Askbot installation

3. Add 'askbot_models_extension' app to the openaction INSTALLED_APPS into 
    the openaction settings file. Include it ABOVE the action app.
