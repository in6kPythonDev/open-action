# Author: Luca Ferroni
# License: AGPLv3

from django.contrib.admin import helpers
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from django.template import Template
from django.template.response import TemplateResponse

from django.views.generic import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

import logging, traceback

log = logging.getLogger(settings.PROJECT_NAME)

# Naive implementation to be tuned as data protocol exchange for Ajax requests
template_success = Template("""
    <div id="response" class="success" {{ extra_attrs }}>{{ msg }}</div>
""")

template_error = Template("""
    <div id="response" class="error" {{ extra_attrs }}>{{ msg }}</div>
""")

HTTP_ERROR_INTERNAL = 505
HTTP_SUCCESS = 200
HTTP_REDIRECT = 302

def response_error(request, msg="error", on_complete=""):
    context = { 
        'msg' : msg,
        'http_status_code' : HTTP_ERROR_INTERNAL,
        'exception_type' : type(msg),
        'exception_msg' : unicode(msg),
    }
    if on_complete:
        context['extra_attrs'] = 'on_complete="%s"' % on_complete
    return TemplateResponse(request, template_error, context)

def response_success(request, msg="ok", on_complete=""):
    context = { 
        'msg' : msg,
        'http_status_code' : HTTP_SUCCESS,
    }
    if on_complete:
        context['extra_attrs'] = 'on_complete="%s"' % on_complete
    return TemplateResponse(request, template_success, context)

def response_redirect(request, url):
    context = { 
        'http_status_code' : HTTP_REDIRECT,
    }
    return TemplateResponse(request, template_success, context)

#--------------------------------------------------------------------------------

class ResponseWrappedView(View):
    """Wrap the dispatcher in order to apply Ajax protocol for data exchange.

    Used also as entry point for logging.

    Now can be implemented also as a Middleware. 
    Let's see if we need some more customization or not...
    """

    def dispatch(self, request, *args, **kwargs):

        view_name = self.__class__.__name__.lower()
        method = request.method.upper()
        log.debug("%s:%s user %s args=%s kw=%s" % (
            view_name, method, request.user, args, kwargs
        ))
        try:
            rv = super(ResponseWrappedView, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            log.debug("%s:%s user %s exception raised %s tb=%s" % (
                view_name, method, request.user, e, traceback.format_exc()
            ))
            if request.is_ajax():
                rv = response_error(request, msg=e)
            else:
                raise
        return rv
        

class LoginRequiredView(ResponseWrappedView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(*args, **kwargs)

