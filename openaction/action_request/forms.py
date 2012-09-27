from django import forms

from askbot.models.user import User
from action.models import Action

class ModerationForm(forms.Form):

    follower = forms.ModelChoiceField(required=True,
        queryset= Action.objects.all()
    )

    request_text = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', None)
 
        followers_not_moderators = action.thread.followed_by.all().exclude(pk__in=action.moderator_set.all())

        ModerationForm.base_fields['follower'].queryset = followers_not_moderators
        super(ModerationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ModerationForm, self).clean()
        user_pk = self.data['follower']
        cleaned_data['follower'] = User.objects.get(pk=user_pk)
        return self.cleaned_data

class ModerationProcessForm(forms.Form):

    CHOICES = (
        (0, 'Rifiuto'),
        (1, 'Accetto'),
    )

    accept_request = forms.ChoiceField(required=True, choices=CHOICES)

    answer_text = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(ModerationProcessForm, self).clean()
        accepted = self.data['accept_request']
        #print "errors=%s\n" % self.errors
        cleaned_data['accept_request'] = int(accepted)
        return self.cleaned_data

