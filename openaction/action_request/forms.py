from django import forms

from askbot.models.user import User
from action.models import Action

class ModerationForm(froms.Form):

    follower = forms.ModelChoiceField(required=True,
        queryset=()
    )

    request_text = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        action = kw.pop('action', None)
        
        followers_not_moderators = action.thread.followed_by.all().exclude(pk__in=action.moderator_set.all())

        ModerationForm.base_fields['follower'].queryset = queryset
        super(ModerationForm, self).__init__(*args, **kwargs)


class ModerationProcessForm(froms.Form):

    answer_text = forms.CharField(required=False)

