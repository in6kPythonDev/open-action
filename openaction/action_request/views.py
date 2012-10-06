from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.db import transaction

import askbot.utils.decorators as askbot_decorators
from action_request import forms as action_request_forms
from action.models import Action
from action_request.models import ActionRequest
from action_request.signals import action_moderation_request_submitted, action_moderation_request_processed
from action_request import consts
from action import const as a_consts

from lib import views_support


class ActionRequestView(FormView, SingleObjectMixin, views_support.LoginRequiredView):
    """ A User submits a request of some type to another user
    with regard to an Action"""

    model = Action

    @method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionRequestView, self).dispatch(request, *args, **kwargs)

class ActionSetStatusRequestView(ActionRequestView):
    """ Action owner asks to the Staff to set Action status """

    form_class = action_request_forms.SetStatusForm
    template_name = 'status/change.html'

    def form_valid(self, form):

        sender = self.request.user
        action = self.get_object()

        message = form.cleaned_data['request_text']
        status = form.cleaned_data['status_to_set']

        if status in (a_consts.ACTION_STATUS_VICTORY,):
            request_type = consts.REQUEST_TYPE['vict']
        elif status in (a_consts.ACTION_STATUS_CLOSED,):
            request_type = consts.REQUEST_TYPE['clos']

        sender.assert_can_ask_action_status_update(sender, 
            action,
            request_type
        )

        action_request = ActionRequest(
            action=action,
            sender=sender,
            request_notes=message,
            request_type=request_type 
        )
        action_request.save()
        
        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)
        

class ActionMessageRequestView(ActionRequestView):
    """ Send a message about the Action to a User """

    form_class = action_request_forms.MessageForm
    template_name = 'private_message/send.html'

    def get_form_kwargs(self):
        kwargs = super(ActionRequestView, self).get_form_kwargs()
        kwargs['action'] = self.get_object()
        return kwargs

    @transaction.commit_on_success
    def form_valid(self, form):

        sender = self.request.user
        action = self.get_object()

        recipient = form.cleaned_data['referrer']
        message = form.cleaned_data['message_text']
        request_type = consts.REQUEST_TYPE['msg']

        sender.assert_can_request_moderation_for_action(sender, recipient, action)

        action_request = ActionRequest(action=action,
            sender=sender,
            recipient=recipient,
            request_notes=request_notes,
            request_type=request_type 
        )
        action_request.save()

        action_message_sent.send(sender=action_request)

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

class ActionModerationRequestView(ActionRequestView):
    """ Submit a request for an Action moderation to a follower of the Action 
    to moderate"""

    form_class = action_request_forms.ModerationForm
    template_name = 'moderation/add.html'

    def get_form_kwargs(self):
        kwargs = super(ActionRequestView, self).get_form_kwargs()
        kwargs['action'] = self.get_object()
        return kwargs

    @transaction.commit_on_success
    def form_valid(self, form):

        sender = self.request.user
        action = self.get_object()

        recipient = form.cleaned_data['follower']
        request_notes = form.cleaned_data['request_text']
        request_type = consts.REQUEST_TYPE['mod']

        sender.assert_can_request_moderation_for_action(sender, recipient, action)

        action_request = ActionRequest(action=action,
            sender=sender,
            recipient=recipient,
            request_notes=request_notes,
            request_type=request_type 
        )
        action_request.save()

        action_moderation_request_submitted.send(sender=action_request)

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

class ActionRequestProcessView(FormView, SingleObjectMixin, views_support.LoginRequiredView):
    """ A User decides to accept or refuse an ActionRequest sent to him 
    by another User"""
    
    model = ActionRequest

    @method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionRequestProcessView, self).dispatch(request, *args, **kwargs)

class ActionRequestMessageResponseView(ActionRequestProcessView):

    form_class = action_request_forms.MessageResponseForm
    template_name = 'private_message/reply.html'

    #transaction.commit_on_success
    def form_valid(self, form):

        user = self.request.user
        action_request = self.get_object()
        action = action_request.action
        message_response = form.cleaned_data['message_text']

        user.assert_can_reply_to_action_message(action_request)

        action_request.is_processed = True
        action_request.is_accepted = True
        action_request.answer_notes = message_response
        action_request.save()

        action_message_received.send(sender=action_request)
 
        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

class ActionRequestModerationProcessView(ActionRequestProcessView):
    """ A User decides to accept or refuse a moderation request sent to him 
    by another User"""

    form_class = action_request_forms.ModerationProcessForm
    template_name = 'moderation/process.html'

    @transaction.commit_on_success
    def form_valid(self, form):

        user = self.request.user
        action_request = self.get_object()
        action = action_request.action
        accepted = form.cleaned_data['accept_request']
        answer_notes = form.cleaned_data['answer_text']

        can_accept = user.assert_can_process_moderation_for_action(action_request)

        action_request.is_processed = True
        action_request.is_accepted = [False, [False, True][accepted=='1']][can_accept]
        print("action_request is accepted: %s" % action_request.is_accepted)
        action_request.answer_notes = answer_notes
        action_request.save()

        if action_request.is_accepted:
            print("action.moderator_set.add(user)")
            action.moderator_set.add(user)
            #KO: this is not needed action.save()

        action_moderation_request_processed.send(sender=action_request
            #moderator=user
        )

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)
