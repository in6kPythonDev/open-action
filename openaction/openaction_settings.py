"""Just some notes. Cut&Paste content to settings.py. Usually we use default_settings.py"""

import settings

#--------------------------------------------------------------------------------
# Social auth authentication

LOGIN_URL          = '/social_auth/login-form/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/social_auth/login-error/'

# Taken from open_municipio social-auth integration

FACEBOOK_EXTENDED_PERMISSIONS = ['email'] # if this is missing, only username is retrieved
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_RAISE_EXCEPTIONS = settings.DEBUG
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'oa_social_auth.pipeline.redirect_to_form',
    'oa_social_auth.pipeline.extra_data',
    'social_auth.backends.pipeline.user.create_user',
    'oa_social_auth.pipeline.create_profile',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
)

AUTH_PROFILE_MODULE = 'users.UserProfile'


# End "taken from"


AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
) + settings.AUTHENTICATION_BACKENDS

TWITTER_CONSUMER_KEY         = ''
TWITTER_CONSUMER_SECRET      = ''
FACEBOOK_APP_ID              = ''
FACEBOOK_API_SECRET          = ''
LINKEDIN_CONSUMER_KEY        = ''
LINKEDIN_CONSUMER_SECRET     = ''
ORKUT_CONSUMER_KEY           = ''
ORKUT_CONSUMER_SECRET        = ''
GOOGLE_CONSUMER_KEY          = ''
GOOGLE_CONSUMER_SECRET       = ''
GOOGLE_OAUTH2_CLIENT_ID      = ''
GOOGLE_OAUTH2_CLIENT_SECRET  = ''
FOURSQUARE_CONSUMER_KEY      = ''
FOURSQUARE_CONSUMER_SECRET   = ''
VK_APP_ID                    = ''
VK_API_SECRET                = ''
LIVE_CLIENT_ID = ''
LIVE_CLIENT_SECRET = ''
SKYROCK_CONSUMER_KEY      = ''
SKYROCK_CONSUMER_SECRET   = ''
YAHOO_CONSUMER_KEY        = ''
YAHOO_CONSUMER_SECRET     = ''

LOGIN_URL          = '/login-form/'
LOGIN_REDIRECT_URL = '/logged-in/'
LOGIN_ERROR_URL    = '/login-error/'

TEMPLATE_CONTEXT_PROCESSORS = settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
    'django.core.context_processors.static',
    'base.context.global_context',
)

#--------------------------------------------------------------------------------

INSTALLED_APPS = list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('base')
INSTALLED_APPS.append('django.contrib.humanize')
INSTALLED_APPS.append('askbot_extensions')
INSTALLED_APPS.append('organization')
INSTALLED_APPS.append('action')
INSTALLED_APPS.append('social_auth')
INSTALLED_APPS.append('oa_social_auth')
INSTALLED_APPS.append('external_resource')
INSTALLED_APPS.append('friendship')
INSTALLED_APPS.append('notification')
INSTALLED_APPS.append('oa_notification')
INSTALLED_APPS.append('action_request')
INSTALLED_APPS.append('users')
INSTALLED_APPS.append('ajax_select')


PROJECT_NAME = "openaction"

# A sample logging configuration. 
LOG_FILE = settings.PROJECT_ROOT + '/log/%s.log' % PROJECT_NAME
LOG_FILE_DEBUG = settings.PROJECT_ROOT + '/log/%s_debug.log' % PROJECT_NAME
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

REFERRAL_TOKEN_RESET_TIMEOUT_DAYS = 5

MAX_MODERATION_REQUESTS = 3
MAX_DELIVERABLE_MESSAGES = 3

#--------------------------------------------------------------------------------

DEFAULT_FROM_EMAIL = "openaction@localhost.befair.it"
NOTIFICATION_BACKENDS = (
    ("email", "notification.backends.email.EmailBackend"),
    #("facebook_inbox", "oa_notification.backends.facebook.FBInboxBackend"),
    
    ("openaction", "oa_notification.backends.openaction.OpenActionDefaultBackend"), #IMPORTANT: The openaction backend is REQUIRED!
    #("twitter_message", "oa_notification.backends.twitter.TWMessageBackend"),
)

#--------------------------------------------------------------------------------

EXTERNAL_API_BACKENDS_D = {
    "facebook" : "external_resource.backends.FBResourceBackend",
    #"twitter" : "external_resource.backends.TwitterResourceBackend",
    "cityreps" : {
        'ENGINE' : "external_resource.backends.openpolis.OpenPolisCityrepsBackend",
        'HOST' : 'api.openpolis.it',
        'PORT' : 80,
        'PROTOCOL': 'http',
        'BASE_PATH' : '/op/1.0/',
        'USER' : 'your_user_here',
        'PASSWORD' : 'your_password_here',
    },
    "locations" : {
        'ENGINE' : "external_resource.backends.openpolis.OpenPolisLocationsBackend",
        'HOST' : 'api.openpolis.it',
        'PORT' : 80,
        'PROTOCOL': 'http',
        'BASE_PATH' : '/op/1.0/',
        'USER' : 'your_user_here',
        'PASSWORD' : 'your_password_here',
    },
    "politicians" : {
        'ENGINE' : "external_resource.backends.openpolis.OpenPolisPoliticiansBackend",
        'HOST' : 'api.openpolis.it',
        'PORT' : 80,
        'PROTOCOL': 'http',
        'BASE_PATH' : '/op/1.0/',
        'USER' : 'your_user_here',
        'PASSWORD' : 'your_password_here',
    },
}

# Map correspondance of backend names from social_auth to external_resource
SOCIAL_AUTH_TO_EXTERNAL_RESOURCE_BACKEND_MAP = {
    "facebook" : "facebook",
}

#Time after that an ExternalResource has to be updated
MAX_TIME_ELAPSED = 10

#---------------------------------------------------------------------------------
# Redis cache server

# IP:PORT address. None will use default values
REDIS_SERVER_ADDR = None
REDIS_SERVER_PORT = None

# Redis Database identifier. None will use default values
REDIS_DATABASE    = None

#---------------------------------------------------------------------------------
# Ajax select

AJAX_LOOKUP_CHANNELS = {
    'geonamechannel' : ( 'action.lookups' , 'GeonameLookup'),
    'politicianchannel' : ( 'action.lookups', 'PoliticianLookup'),
    'cityrepchannel' : ( 'action.lookups', 'CityrepLookup'),
}
# magically include jqueryUI/js/css
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'


