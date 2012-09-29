# -*- coding: utf-8 -*-

from django import forms
import askbot.forms as askbot_forms
from action.models import Geoname, ActionCategory, Politician, Media

class ActionForm(askbot_forms.AskForm):
    # TOASK: Ajaxification of fields autocomplete?

    in_nomine = forms.ChoiceField(required=True,
        choices=() #will be set in __init__
    )

    geoname_set = forms.ModelMultipleChoiceField(
        queryset=Geoname.objects, label="Territori",
        required=False
    )
    category_set = forms.ModelMultipleChoiceField(
        queryset=ActionCategory.objects, label=u"Ambiti",
        required=False,
        help_text=u"La scelta degli ambiti può aiutarti a definire meglio i prossimi passi"
    )
    politician_set = forms.ModelMultipleChoiceField(
        queryset=Politician.objects, label="Politici",
        required=False
    )
    media_set = forms.ModelMultipleChoiceField(
        queryset=Media.objects, label="Media",
        required=False
    ) 

    def __init__(self, request, *args, **kw):
        user = request.user
        choices = [("user-%s" % user.pk, user),]
        orgs = user.orgs_represented
        for org in orgs:
            choices.append(
                ("org-%s" % org.pk, org)
            )
        ActionForm.base_fields['in_nomine'].choices = choices
        super(ActionForm, self).__init__(*args, **kw)
        if not orgs:
            self.hide_field('in_nomine')
        

class EditActionForm(askbot_forms.EditQuestionForm):
    # TOASK: Ajaxification of fields autocomplete?

    geoname_set = forms.ModelMultipleChoiceField(
        queryset=Geoname.objects, label="Territori",
        required=False
    )
    category_set = forms.ModelMultipleChoiceField(
        queryset=ActionCategory.objects, label="Categorie",
        required=False
    )
    politician_set = forms.ModelMultipleChoiceField(
        queryset=Politician.objects, label="Politici",
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

