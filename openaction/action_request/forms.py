from django import forms

from askbot.models.user import User
from action import const as a_consts

class ModerationForm(forms.Form):

    follower = forms.ModelChoiceField(required=True,
        queryset=User.objects.none()
    )

    request_text = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action')
 
        #WAS: followers = action.thread.followed_by.all()
        followers = action.followers
        followers_not_moderators = followers.exclude(pk__in=action.moderator_set.all())

        super(ModerationForm, self).__init__(*args, **kwargs)
        self.fields['follower'].queryset = followers_not_moderators

class ModerationProcessForm(forms.Form):

    CHOICES = (
        (0, 'Rifiuto'),
        (1, 'Accetto'),
    )

    accept_request = forms.ChoiceField(required=True, choices=CHOICES)

    #WAS: forms has no attribute TextField 
    #WAS: answer_text = forms.TextField(required=False)
    answer_text = forms.CharField(required=False)

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

class MessageForm(forms.Form):

    #referrer = forms.ModelChoiceField(required=True,
    #    queryset=User.objects.none()
    #)

    message_text = forms.CharField(required=False)

    #def __init__(self, *args, **kwargs):
    #    action = kwargs.pop('action')
 
    #    referrers = action.referrers

    #    super(MessageForm, self).__init__(*args, **kwargs)
    #    self.fields['referrer'].queryset = referrers

class MessageResponseForm(forms.Form):

    message_text = forms.CharField()

class SetStatusForm(forms.Form):

    CHOICES = (
        (a_consts.ACTION_STATUS_VICTORY, 'Vittoria'),
        (a_consts.ACTION_STATUS_CLOSED, 'Chiusura'),
    )

    status_to_set = forms.ChoiceField(required=True, choices=CHOICES)

    request_text = forms.CharField(required=False)

