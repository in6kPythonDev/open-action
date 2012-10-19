from django.conf import settings
from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User

from users.forms import UserRegistrationForm
from users.models import UserProfile

from registration.signals import user_registered
from registration.signals import user_activated

from django.dispatch import receiver

# TODO Matteo: transform connect to receivers decorators
# user_registered.connect(user_created)
# user_activated.connect(log_in_user)


"""
Functions listed below act as receivers and are used along the
registration workflow.
"""

@receiver(user_registered):#, sender=DefaultBackend or sender=SimpleBackend
def user_created(sender, user, request, **kwargs):
    """
    As soon as a new ``User`` is created, the correspondent
    ``UserProfile`` must be created too. Necessary information is
    supposed to be found in POST data.
    """
    # LF QUESTION: form.data instead of form.cleaned_data, to not call twice form.is_valid?
    # LF QUESTION: why tos and pri are not saved in the db?
    form = UserRegistrationForm(request.POST)
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    user.save()
    
    extra_data = UserProfile(user=user)
    extra_data.says_is_politician = form.cleaned_data['says_is_politician']
    extra_data.uses_nickname = form.cleaned_data['uses_nickname']
    extra_data.privacy_level = UserProfile._meta.get_field_by_name('privacy_level')[0].default #LF form.cleaned_data['privacy_level']
    extra_data.wants_newsletter = False
    if 'wants_newsletter' in request.POST:
        extra_data.wants_newsletter = form.cleaned_data['wants_newsletter']
    extra_data.city = form.cleaned_data['city']
    extra_data.save()
   
@receiver(user_activated):#, sender=DefaultBackend or sender=SimpleBackend
def log_in_user(sender, user, request, **kwargs):
    """
    Dirty trick to let the user automatically logged-in at the end of
    the registration process.
    """
    if getattr(settings, 'REGISTRATION_AUTO_LOGIN', False):
        backend = get_backends()[0] # A bit of a hack to bypass `authenticate()`.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, user)

