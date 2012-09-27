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

        print "followers %s" % followers_not_moderators

        ModerationForm.base_fields['follower'].queryset = followers_not_moderators
        super(ModerationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ModerationForm, self).clean()
        user_pk = self.data['follower']
        self.cleaned_data['follower'] = User.objects.get(pk=user_pk)
        return self.cleaned_data

class ModerationProcessForm(forms.Form):

    answer_text = forms.CharField(required=False)

