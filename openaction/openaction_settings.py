"""Just some notes. Cut&Past to settings.py. Usually we use default_settings.py"""

import settings

INSTALLED_APPS = list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('askbot_models_extension')
INSTALLED_APPS.append('action')


PROJECT_NAME = "openaction"

# A sample logging configuration. 
LOG_FILE = PROJECT_ROOT + '/log/%s.log' % PROJECT_NAME
LOG_FILE_DEBUG = PROJECT_ROOT + '/log/%s_debug.log' % PROJECT_NAME
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logfile':{
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 1048576,
            'backupCount' : 5,
            'formatter': 'simple'
        },
        'logfile_debug':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_DEBUG,
            'maxBytes': 1048576,
            'backupCount' : 10,
            'formatter': 'verbose'
        },
#        'mail_admins': {
#            'level': 'ERROR',
#            'class': 'django.utils.log.AdminEmailHandler',
#        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        PROJECT_NAME: {
            'handlers': ['console', 'logfile', 'logfile_debug'],
            'level': 'DEBUG',
        }
    }
}
