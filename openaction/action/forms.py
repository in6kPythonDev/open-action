# -*- coding: utf-8 -*-

from django import forms
import askbot.forms as askbot_forms
from action.models import Action, Geoname, ActionCategory, Politician, Media
from askbot.models import User
from django.core import exceptions
from external_resource.models import ExternalResource

from ajax_select import make_ajax_field
from ajax_select import get_lookup

MAP_FIELD_NAME_TO_CHANNEL = {
    'geoname_set' : 'geonamechannel', 
    'politician_set' : 'politicianchannel',
    'media_set' : 'TODO',
}

CITYREP_CHANNEL_NAME = 'cityrepchannel'

INSTITUTIONS = {
    'comune' : ['consiglio','giunta',],
    'provincia' : ['consiglio','giunta',],
    'regione' : ['consiglio','giunta',],
    'senato' : ['representatives',],
    'europarl' : ['representatives',],
    'camera' : ['representatives',],
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
    media_set = forms.ModelMultipleChoiceField(
        queryset=Media.objects, label="Media",
        required=False
    ) 

    def __init__(self, request, *args, **kw):
        if kw.get('action'):
            self.action = kw.pop('action')
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

    def _clean_geoname_set(self, cleaned_data):
        """Return a representation of Geoname objects based on 
        the data contained into an external API"""
        #This is _clean method because it has to be called BEFORE _clean_politician_set

        geoname_ids = cleaned_data.get('geoname_set')

        if geoname_ids:
            field_name = 'geoname_set'
            lookup = get_lookup(MAP_FIELD_NAME_TO_CHANNEL[field_name])
            values = lookup.get_objects(geoname_ids)

            if len(values) != len(geoname_ids):
                for value in values:
                    if value in geoname_ids:
                        values.remove(value)
                #raise exceptions.InvalidGeonameListError(values)
                raise exceptions.ValidationError(u"Non tutti i luoghi sono stati recuperati. Sono rimasti fuori i luoghi con id: %s" % values)
            
        else:
            values = []
        
        return values
        
    def _clean_politician_set(self, cleaned_data, geoname_ids):
        """Return a representation of Politician objects based on 
        the data contained into an external API

        Check that the Total threshold come with the form is equal
        to the sum of politicians threshold deltas  """

        field_name = 'politician_set'
        politician_ids = [int(elem) for elem in cleaned_data[field_name].strip('|').split('|')]
        politician_ids_copy = list(politician_ids)

        if politician_ids:

            for cityrep_id in geoname_ids:
                if not len(politician_ids_copy):
                    break
                found_ids = self.get_politicians_from_cityrep(
                    politician_ids_copy,
                    cityrep_id
                )
                #print("\n\nfound_ids: %s\n" % found_ids)
                for politician_id in found_ids:
                    politician_ids_copy.remove(politician_id)
                
            if len(politician_ids_copy):
                raise exceptions.ValidationError(u"Non tutti i politici sono stati recuperati. Sono rimasti fuori i politici con id: %s" % politician_ids_copy)

            lookup = get_lookup(MAP_FIELD_NAME_TO_CHANNEL[field_name])
            values = lookup.get_objects(politician_ids)

        else:
            values = []

        return values

    def get_politicians_from_cityrep(self, politician_ids, cityrep_id):
        """ Return a list of politicians from a list of city
        representatives """

        lookup = get_lookup(CITYREP_CHANNEL_NAME)
        politicians = []

        cityrep_data = lookup.get_objects([cityrep_id])[0]['city_representatives']

        for institution, institution_kinds in INSTITUTIONS.items():

            for inst_kind in institution_kinds:
                cityreps_of_kind = cityrep_data[institution][inst_kind]

                for politician in cityreps_of_kind:
                    if politician['politician_id'] in politician_ids:
                        politicians.append(politician['politician_id'])

        return politicians

    def check_threshold(self, cleaned_data):
        """ Check that the threshold deltas sum is equal to the given total
        threshold. """

        computed_threshold = 0
        politician_data = cleaned_data['politician_set']
        total_threshold = int(cleaned_data['threshold'])

        for datum in politician_data:

            #compute politician threshold
            threshold_delta = self.compute_threshold_delta(datum)
            computed_threshold = computed_threshold + threshold_delta

        if computed_threshold != total_threshold:
            raise exceptions.ValidationError("La soglia indicata non corrisponde a quella ricavata dai politici scelti")

    def compute_threshold_delta(self, politician_datum):
        return 0
 
    def clean(self):
        """ overriding form clean """
        cleaned_data = super(ActionForm, self).clean()

        cleaned_data['politician_set'] = self.data.get('politician_set',[])
        if self._errors.get('politician_set'):
            del self._errors['politician_set']

        geoname_ids = cleaned_data.get('geoname_set')
        if geoname_ids:
            cleaned_data['geoname_set'] = self._clean_geoname_set(cleaned_data)
        else:
            external_resource_ids = self.action.geonames.values_list('external_resource', flat=True)
            geoname_ids = [external_resource.ext_res_id for external_resource in ExternalResource.objects.filter(pk__in=external_resource_ids)]
 
        if cleaned_data['politician_set']:
            cleaned_data['politician_set'] = self._clean_politician_set(
                cleaned_data,
                geoname_ids
            )
        self.check_threshold(cleaned_data)
        # set defaults
        for field_name in ('category_set', 'media_set'):
            if not cleaned_data.get(field_name):
                cleaned_data[field_name] = []
        return cleaned_data


#class EditActionForm(askbot_forms.EditQuestionForm):
#    # TOASK: Ajaxification of fields autocomplete?
#
#    threshold = forms.CharField()
#
#    geoname_set = make_ajax_field(Action, 
#        label = "Territori",
#        model_fieldname='geoname_set',
#        channel='geonamechannel', 
#        help_text="Search for place by name or by city",
#        required=False,
#    )
#    category_set = forms.ModelMultipleChoiceField(
#        queryset=ActionCategory.objects, label=u"Ambiti",
#        required=False,
#        help_text=u"La scelta degli ambiti può aiutarti a definire meglio i prossimi passi"
#    )
#    politician_set = forms.MultipleChoiceField(
#        label="Politici",
#        required=False
#    )
#    media_set = forms.ModelMultipleChoiceField(
#        queryset=Media.objects, label="Media",
#        required=False
#    ) 

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
