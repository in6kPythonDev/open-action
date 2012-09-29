from django import forms

from askbot.models.user import User

class ModerationForm(forms.Form):

    follower = forms.ModelChoiceField(required=True,
        queryset=User.objects.none()
    )

    request_text = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action')
 
        followers = action.thread.followed_by.all()
        followers_not_moderators = followers.exclude(pk__in=action.moderator_set.all())

        ModerationForm.base_fields['follower'].queryset = followers_not_moderators
        super(ModerationForm, self).__init__(*args, **kwargs)

class ModerationProcessForm(forms.Form):

    CHOICES = (
        (0, 'Rifiuto'),
        (1, 'Accetto'),
    )

    accept_request = forms.ChoiceField(required=True, choices=CHOICES)

    answer_text = forms.TextField(required=False)

    # LESSON: you are simply doing nothing here. :)
    # because you manipulate cleaned_data and return self.cleaned_data.
    # I leave the clean() method commented, read it and then erase this LESSON
    # and the method. In self.cleaned_data['accept_request'] you already find
    # 0 or 1
    #def clean(self):
    #    cleaned_data = super(ModerationProcessForm, self).clean()
    #    accepted = self.data['accept_request']
    #    #print "errors=%s\n" % self.errors
    #    cleaned_data['accept_request'] = int(accepted)
    #    return self.cleaned_data

