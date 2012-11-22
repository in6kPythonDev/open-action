from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.db import transaction

import askbot.utils.decorators as askbot_decorators
from action_request import forms as action_request_forms
from action.models import Action
from action_request.models import ActionRequest
from action_request.signals import (action_moderation_request_submitted, 
    action_moderation_request_processed,
    action_message_sent,
    action_message_replied
)
from action_request import consts
from action import const as a_consts

from lib import views_support


class ActionRequestView(FormView, SingleObjectMixin, views_support.LoginRequiredView):
    """ A User submits a request of some type to another user
    with regard to an Action"""

    model = Action

    #@method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionRequestView, self).dispatch(request, *args, **kwargs)

class ActionSetStatusRequestView(ActionRequestView):
    """ An Action referrer asks to the Staff to set Action status """

    form_class = action_request_forms.SetStatusForm
    template_name = 'status/change.html'

    def form_valid(self, form):

        sender = self.request.user
        action = self.get_object()

        message = form.cleaned_data['request_text']
        status = form.cleaned_data['status_to_set']

        if status in (a_consts.ACTION_STATUS_VICTORY,):
            request_type = consts.REQUEST_TYPE_SET_VICTORY
        elif status in (a_consts.ACTION_STATUS_CLOSED,):
            request_type = consts.REQUEST_TYPE_SET_CLOSURE

        sender.assert_can_ask_action_status_update(
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
    """ A User send a message about the Action to the Action referrers """

    form_class = action_request_forms.MessageForm
    template_name = 'private_message/send.html'

    #def get_form_kwargs(self):
    #    kwargs = super(ActionMessageRequestView, self).get_form_kwargs()
    #    kwargs['action'] = self.get_object()
    #    return kwargs

    @transaction.commit_on_success
    def form_valid(self, form):

        sender = self.request.user
        action = self.get_object()

        #recipient = form.cleaned_data['referrer']
        recipient = action.referrers
        message = form.cleaned_data['message_text']
        request_type = consts.REQUEST_TYPE_MESSAGE

        sender.assert_can_send_action_message(sender, 
            recipient, 
            action
        )

        action_request = ActionRequest(
            action=action,
            sender=sender,
            request_notes=message,
            request_type=request_type 
        )
        action_request.save()
        action_request.recipient_set.add(*recipient)
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
        request_type = consts.REQUEST_TYPE_MODERATION

        sender.assert_can_request_moderation_for_action(sender, recipient, action)
        #print("RECIPIENT: %s", recipient)
        action_request = ActionRequest(
            action=action,
            sender=sender,
            request_notes=request_notes,
            request_type=request_type 
        )
        action_request.save()
        action_request.recipient_set.add(recipient)
        action_request.save()

        action_moderation_request_submitted.send(sender=action_request)

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

class ActionRequestProcessView(FormView, SingleObjectMixin, views_support.LoginRequiredView):
    """ A User decides to accept or refuse an ActionRequest sent to him 
    by another User """
    
    model = ActionRequest

    #@method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionRequestProcessView, self).dispatch(request, *args, **kwargs)

class ActionRequestMessageResponseView(ActionRequestProcessView):
    """ An Action referrer reply to a message sent to a User about the Action 
    he is referring. 

    When a referer reply, the user woho sent the message and all the other
    referrers are notified of this. 
    """
    
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

        action_message_replied.send(sender=action_request, replier=user)
 
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

        user.assert_can_process_moderation_for_action(action_request)

        action_request.is_processed = True
        #NOTE: weird behaivour. Cleaned data for accepted return a string 
        action_request.is_accepted = [False, True][accepted=='1']
        #print("action_request is accepted: %s" % action_request.is_accepted)
        action_request.answer_notes = answer_notes
        action_request.save()


        if action_request.is_accepted:
            #print("action.moderator_set.add(user)")
            action.moderator_set.add(user)

        # For all same request_types ActionRequest --> 
        # set processed, is_accepted, 
        # and in answer_notes write ("processed with #action_request.pk")
        # QUESTION: Is this true only for accepted requests or for not 
        # accepted requests too?
        duplicate_requests = action_request.get_same_request_types().exclude(pk=action_request.pk)

        for request in duplicate_requests:
            request.is_processed = True
            request.is_accepted = action_request.is_accepted
            request.answer_notes = "moderation request processed and %s accepted with action_request %s" % (action_request.pk, ["","not"][not action_request.is_accepted])
            request.save()

        action_moderation_request_processed.send(sender=action_request
            #moderator=user
        )

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)
