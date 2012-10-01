from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.messages.api import get_messages
from django.utils.translation import ugettext as _

from social_auth import __version__ as version
from social_auth.utils import setting


def home(request):
    """Home view, displays login mechanism"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('done')
    else:
        return render_to_response('home.html', {'version': version},
                                  RequestContext(request))


@login_required
def done(request):
    """Login complete view, displays user data"""
    ctx = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend')
    }
    return render_to_response('done.html', ctx, RequestContext(request))


def error(request):
    """Error view"""
    messages = get_messages(request)
    return render_to_response('error.html', {'version': version,
                                             'messages': messages},
                              RequestContext(request))


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')


# Taken from OpenMunicipio social_auth integration code (om_auth application)
from users.forms import UserSocialRegistrationForm, ProfileSocialRegistrationForm

def login_form(request):
    """
    When a user registers through a social network we need some
    additional information.
    """
    error = None
    if request.method == 'POST':
        profile_form = ProfileSocialRegistrationForm(request.POST)
        user_form = UserSocialRegistrationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            session_variable = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
            request.session['saved_username'] = user_form.cleaned_data['username']
            #LF: request.session['saved_privacy_level'] = profile_form.cleaned_data['privacy_level']
            request.session['saved_wants_newsletter'] = profile_form.cleaned_data['wants_newsletter']
            request.session['saved_city'] = profile_form.cleaned_data['city']
            request.session['saved_uses_nickname'] = profile_form.cleaned_data['uses_nickname']
            request.session['saved_says_is_politician'] = profile_form.cleaned_data['says_is_politician']
            backend = request.session[session_variable]['backend']
            return redirect('socialauth_complete', backend=backend)
        else:
            error = _('Form is invalid')

    else:
        user_form = UserSocialRegistrationForm()
        profile_form = ProfileSocialRegistrationForm()

    return render_to_response('login_form.html', {
            'error': error,
            'user_form': user_form,
            'profile_form': profile_form,
            }, RequestContext(request))


