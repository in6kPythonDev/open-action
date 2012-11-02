# -*- coding: utf-8 -*-

from django import forms
import askbot.forms as askbot_forms
from action.models import Action, Geoname, ActionCategory, Politician, Media
from askbot.models import User

from ajax_select import make_ajax_field
from ajax_select import get_lookup

MAP_FIELD_NAME_TO_CHANNEL = {
    'geoname_set' : 'geonamechannel', 
    'politician_set' : 'politicianchannel',
    'media_set' : 'TODO',
}

class ActionForm(askbot_forms.AskForm):
    # TOASK: Ajaxification of fields autocomplete?

    in_nomine = forms.ChoiceField(required=True,
        choices=() #will be set in __init__
    )

    threshold = forms.CharField()

    geoname_set = make_ajax_field(Action, 
        label = "Territori",
        model_fieldname='geoname_set',
        channel='geonamechannel', 
        help_text="Search for place by name or by city",
        required=False,
    )
    category_set = forms.ModelMultipleChoiceField(
        queryset=ActionCategory.objects, label=u"Ambiti",
        required=False,
        help_text=u"La scelta degli ambiti può aiutarti a definire meglio i prossimi passi"
    )
    politician_set = forms.MultipleChoiceField(
        label="Politici",
        required=False
    )
    #politician_set = forms.ModelMultipleChoiceField(
    #    queryset=Politician.objects, label="Politici",
    #    required=False
    #)
    media_set = forms.ModelMultipleChoiceField(
        queryset=Media.objects, label="Media",
        required=False
    ) 

    def __init__(self, request, *args, **kw):
        user = request.user
        choices = [("user-%s" % user.pk, user),]
        orgs = user.represented_orgs
        for org in orgs:
            choices.append(
                ("org-%s" % org.pk, org)
            )
        super(ActionForm, self).__init__(*args, **kw)
        self.fields['in_nomine'].choices = choices
        if not orgs:
            self.hide_field('in_nomine')

    def clean_geoname_set(self):

        geoname_ids = self.cleaned_data['geoname_ids']

        if geoname_ids:
            field_name = 'geoname_set'
            lookup = get_lookup(MAP_FIELD_NAME_TO_CHANNEL[field_name])
            json_values = lookup.get_objects(geoname_ids)

            if len(json_values) != len(geoname_ids):
                raise ValidationError("non tutti i geoname sono stati recuperati. Sono rimasti fuori...") #TODO: Matteo
            
        else:
            json_values = []
        
        return json_values
        

    def clean(self):
        """ overriding form clean """
        #dummy implementation
        cleaned_data = super(ActionForm, self).clean()

        # set defaults
        for field_name in ('geoname_set', 'category_set', 
            'politician_set', 'media_set'):
            if not cleaned_data.get(field_name):
                cleaned_data[field_name] = []

        #print("\ncleaned data: %s\n" % cleaned_data)
        #print("\nerrors: %s\n" % self._errors)
        #KLUDGE
        if 'politician_set' in self._errors.keys():
            cleaned_data['politician_set'] = self.data['politician_set']
            del self._errors['politician_set']

        return cleaned_data


class EditActionForm(askbot_forms.EditQuestionForm):
    # TOASK: Ajaxification of fields autocomplete?

    threshold = forms.CharField()

    geoname_set = make_ajax_field(Action, 
        label = "Territori",
        model_fieldname='geoname_set',
        channel='geonamechannel', 
        help_text="Search for place by name or by city",
        required=False,
    )
    category_set = forms.ModelMultipleChoiceField(
        queryset=ActionCategory.objects, label=u"Ambiti",
        required=False,
        help_text=u"La scelta degli ambiti può aiutarti a definire meglio i prossimi passi"
    )
    politician_set = forms.MultipleChoiceField(
        label="Politici",
        required=False
    )
    media_set = forms.ModelMultipleChoiceField(
        queryset=Media.objects, label="Media",
        required=False
    ) 

#----------------------------------------------------------------------------------

class SingleTextareaForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

class ActionCommentForm(SingleTextareaForm):
    pass

class BlogpostCommentForm(SingleTextareaForm):
    pass

class ActionBlogpostForm(SingleTextareaForm):
    pass

#--------------------------------------------------------------------------------

class ModeratorRemoveForm(forms.Form):

    moderator = forms.ModelChoiceField(required=True,
        queryset=User.objects.none()
    )

    #text = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action')
 
        #WAS: followers = action.thread.followed_by.all()
        moderators = action.moderator_set.all()

        super(ModeratorRemoveForm, self).__init__(*args, **kwargs)
        self.fields['moderator'].queryset = moderators
