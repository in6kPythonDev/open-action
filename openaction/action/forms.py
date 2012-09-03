
from django import forms
import askbot.forms as askbot_forms
from action.models import Geoname, ActionCategory

class ActionForm(askbot_forms.AskForm):
    # TOASK: Ajaxification of fields autocomplete?

    geoname_set = forms.ModelMultipleChoiceField(
        queryset=Geoname.objects, label="Territori",
        required=False
    )
    category_set = forms.ModelMultipleChoiceField(
        queryset=ActionCategory.objects, label="Categorie",
        required=False
    )

class ActionCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)

