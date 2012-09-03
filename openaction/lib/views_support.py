# Author: Luca Ferroni
# License: AGPLv3

from django.contrib.admin import helpers
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from django.template import Template
from django.template.response import TemplateResponse

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


