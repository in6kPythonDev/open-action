# NOT USED
# NOT USED
# NOT USED
# NOT USED
# NOT USED
# NOT USED
# NOT USED
# NOT USED
# NOT USED
# NOT USED
# NOT USED
"""
An external resource is a resource that rely on external origin.

This is clear, but when we are updating such a resource in a form,
we have also to define the policy to apply when we manage such a resource.

There are some kinds of policy available to retrieve information from source:

* OVERRIDE_ALL: replace local info with remote info
* OVERRIDE_REMOTE_FIELDS: replace only info that have no specific field in external resource model
* OVERRIDE_NONE: check only if remote resource id exist, but do not update any related field

Fields included in this file are bound to a model which is has an `external_resource` attribute as foreign key to the external resource.
"""

from django import forms

class ExternalResourceField(forms.Field):


    pass

class ExternalResourceMultipleChoiceField(forms.MultipleChoiceFielp):
    pass
