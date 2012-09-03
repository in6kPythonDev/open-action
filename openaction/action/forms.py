from django import forms

class ActionCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
