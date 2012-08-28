import settings

INSTALLED_APPS = list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('askbot_models_extension')
INSTALLED_APPS.append('action')


