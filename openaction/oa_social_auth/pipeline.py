# Taken almost "as is" from OpenMunicipio
# https://github.com/openpolis/open_municipio/blob/django-social-auth-dev/open_municipio/om_auth/pipeline.py

"""
Functions listed below are used in ``django-social-auth``
pipeline. Pipeline is the series of steps users walk through to log in
on OpenMunicipio with their social accounts.
"""

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from users.models import UserProfile

from django.conf import settings

import logging

log = logging.getLogger(settings.PROJECT_NAME)

def redirect_to_form(*args, **kwargs):
    """
    Non-registered users will be prompted a few questions so that
    their OpenMunicipio account is created.
    """
    if not kwargs['request'].session.get('saved_username') and \
       kwargs.get('user') is None:
        return HttpResponseRedirect(reverse('login-form'))

get_profile_field_default = lambda x : UserProfile._meta.get_field_by_name(x)[0].default

def extra_data(request, *args, **kwargs):
    """
    Extra data we need to collect to populate user's profile.
    """
    if kwargs.get('user'):
        username = kwargs['user'].username
        profile = kwargs['user'].get_profile()
        privacy_level = profile.privacy_level
        wants_newsletter = profile.wants_newsletter
        city = profile.city
        uses_nickname = profile.uses_nickname
        says_is_politician = profile.says_is_politician
    else:
        
        username = request.session.get('saved_username')
        privacy_level = request.session.get('saved_privacy_level', 
            get_profile_field_default('privacy_level')
        )
        wants_newsletter = request.session.get('saved_wants_newsletter')
        city = request.session.get('saved_city')
        uses_nickname = request.session.get('saved_uses_nickname')
        says_is_politician = request.session.get('saved_says_is_politician')

    ctx = {
        'username': username,
        'privacy_level': privacy_level,
        'wants_newsletter': wants_newsletter,
        'city': city,
        'uses_nickname' : uses_nickname,
        'says_is_politician' : says_is_politician,
    }
    return ctx


#LF def create_profile(request, user, response, details, is_new=False, *args, **kwargs):
def create_profile(is_new=False, *args, **kwargs):
    """
    Once the user account is created, a profile must be created
    too. (User accounts are Django built-in. Profile is the place we
    store additional information.)
    """
    if is_new:

        #LF get parameter by name, not positional 
        request = kwargs.pop('request')
        user = kwargs.pop('user')
        privacy_level = kwargs.pop('privacy_level')
        wants_newsletter = kwargs.pop('wants_newsletter')
        city = kwargs.pop('city')
        uses_nickname = kwargs.pop('uses_nickname')
        says_is_politician = kwargs.pop('says_is_politician')

        defaults = {
            'privacy_level': privacy_level,
            'wants_newsletter': wants_newsletter,
            'city': city,
            'uses_nickname' : uses_nickname,
            'says_is_politician' : says_is_politician,
        }
        log.debug("DEFAULT profile attrs %s" % defaults)
        log.debug("PIPELINE other args %s %s" % (args, kwargs))
        profile, created = UserProfile.objects.get_or_create(user=user, defaults=defaults)
        #LF not needed according to doc profile.save()

