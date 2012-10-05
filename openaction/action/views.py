from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import transaction

from django.utils.decorators import method_decorator
from django.conf import settings

from askbot.models import Post
from askbot.models.repute import Vote
import askbot.utils.decorators as askbot_decorators
from action.models import Action
from action import const as action_const
from action import forms
from action.signals import action_moderator_removed
from askbot_extensions import utils as askbot_extensions_utils
from organization.models import Organization
import exceptions

from lib import views_support

import logging, datetime

log = logging.getLogger(settings.PROJECT_NAME)


class ActionDetailView(DetailView):
    """ List the details of an Action """

    model = Action
    context_object_name="action" 
    template_name="action_detail.html"

    def get_object(self):
        self.instance = super(ActionDetailView, self).get_object()
        # needs to do something here...?
        # POSSIBLE TODO FUTURE: parse token and increment counter "action view suggested by user"
        return self.instance

    def get_context_data(self, **kwargs):
        context = super(ActionDetailView, self).get_context_data(**kwargs)
        # needs to do something here...?
        return context

#---------------------------------------------------------------------------------

class VoteView(SingleObjectMixin, views_support.LoginRequiredView):
    """Add a vote to a post  
      
    **TODO**
    SUCCESSIVAMENTE (ma non lo fare)
    * prenderemo via url HTTP il parametro "token" per capire
      da chi e' stato inviato il link
    """

    def get_referral(self, action):
        """Get referral token from url and return referral User"""

        token = self.request.REQUEST.get('ref_token')
        log.debug("Token_arrived_from_req: %s" % token)
        if token:
            referral = action.get_user_from_token(token)
        else:
            referral = None
        log.debug("FOUND REFERRAL %s" % referral)
        return referral

class ActionVoteView(VoteView):
    """Add a vote to an Action.

    An Action can be voted only from an authenticated User, and only
    if the Action is in a valid state. The valid states are:
        * ready
        * active

    If the condition above are satisfied, the Action score will be incremented 
    by 1 and a new vote will be added to the Action question votes

    This view accepts only POST requests.
    """

    model = Action

    def post(self, request, *args, **kwargs):
        action = self.get_object()
        request.user.assert_can_vote_action(action)

        referral = self.get_referral(action)
        # Check referral
        if referral:
            if referral == request.user:
                # QUESTION TO ASK: what if a user design itself as a referral
                # for its vote? Should the vote be valid or not? Or, should
                # be the user (and the Action referrers) be notified of this?
                log.debug("User %s has itself as the referral for its vote \
                     on the action %s" % (request.user, action))
        action.vote_add(request.user, referral=referral)
        
        return views_support.response_success(request)

class CommentVoteView(VoteView):
    """Add a vote to an Action comment.

    A comment (a Post of type 'comment') can be voted only from an authenticated 
    User, and only if the Action the comment is child of is in a valid state. 
    The valid states are:
        * ready
        * active
        * closed
        * victory

    If the condition above are satisfied, the comment score will be incremented 
    by 1 and a new vote will be added to the comment post votes

    This view accepts only POST requests.
    """
    
    model = Post

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        request.user.assert_can_vote_comment(comment)
        referral = self.get_referral(comment.action)
        askbot_extensions_utils.vote_add(comment, request.user, referral)
        return views_support.response_success(request) 

#---------------------------------------------------------------------------------

class CommentView(FormView, SingleObjectMixin, views_support.LoginRequiredView):
    """ Add a comment to a post"""
    
class ActionCommentView(CommentView):
    """ Add a comment to an Action

    An Action can be commented only from an authenticated User, and only
    if the Action is in a valid state. The valid states are:
        * ready
        * active
        * closed
        * victory

    NOTE: the check above is performed in the Post pre_save()

    If the condition above are satisfied a new comment (a new Post object 
    of type 'comment') will be added to Action Thread
    """

    #to get the object
    model = Action
    template_name = 'comment/add.html'
    form_class = forms.ActionCommentForm

    def form_valid(self, form):
        """ Redirect to get_success_url(). Must return an HttpResponse."""
        action = self.get_object()
        #WAS: return action.comment_add(form.cleaned_data['text'], self.request.user)
        action.comment_add(form.cleaned_data['text'], self.request.user)
        return views_support.response_success(self.request)

class BlogpostCommentView(CommentView):
    """ Add a comment to an action blog post

    A blog post (a Post object of type 'answer') can be commented only if the
    Action related to the Thread that is parent of the blog post is in a valid 
    state. The valid states are:
        * ready
        * active
        * closed
        * victory
    """

    #to get the object
    model = Post
    template_name = 'comment/add.html'
    form_class = forms.BlogpostCommentForm

    def form_valid(self, form):
        """ Redirect to get_success_url(). Must return an HttpResponse."""
        post = self.get_object()
        #WAS: post.comment_add(form.cleaned_data['text'], self.request.user)
        post.add_comment(form.cleaned_data['text'], 
            self.request.user,
            added_at=None, 
            by_email=False
        )
        return views_support.response_success(self.request)

#---------------------------------------------------------------------------------

class BlogpostView(FormView, SingleObjectMixin, views_support.LoginRequiredView):
    pass

class ActionBlogpostView(BlogpostView):
    """Add an article to the Action blog

    An article can be added only from Users who are Action referrers, and only
    if the Action is in a valid status. The valid status are:
        * ready
        * active
        * closed
        * victory
    """

    model = Action
    form_class = forms.ActionBlogpostForm
    template_name = 'blogpost/add.html'
 
    def form_valid(self, form):

        action = self.get_object()
        self.request.user.assert_can_create_blog_post(action)
        action.blog_post_add(form.cleaned_data['text'], self.request.user)
        return views_support.response_success(self.request)


#---------------------------------------------------------------------------------

class EditableParameterView(UpdateView):
    pass
#    """Consente di editare un attributo di un modello.
#
#    * accessibile solo tramite POST
#    * recupera l'istanza del modello Action
#    * fa getattr(instance, "update_%s" % <attr_name>)(value, save=True) 
#    * dove value e' request.POST["value"]
#    per testare:
#    <form method="post" action="/action/1/edit/title">
#        <input type="text" value="nuovo titolo" />
#        <input type="submit" value="submit" />
#    </form>
#
#    * Devi definire in action i metodi update_xxxx (tipo update_title)
#    che prendono come parametro il valore e un flag "save" per capire se devono
#    anche salvarlo istantaneamente.
#    """
#    model = Action
#    form_class = EditActionAttributeForm
#    success_url = ""#The URL to redirect to after the form is processed.
#
#    def get_object(self,queryset=None):
#        """ Return the Action related to the post object """
#        self.post = super(VoteView, self).get_object(queryset)
#        action = self.post.action
#
#        return action
#
#    def post(self, request, *args, **kwargs):
#        if not request.user.is_authenticated():
#            return HttpResponse(request.META['HTTP_REFERER'])
#        self.action = self.get_object()
#        form_class = self.get_form_class()
#        #value has to be taken from a form text_field 
#        #need to define the form
#        
#        return HttpResponse(request.META['HTTP_REFERER'])
#
#    def form_valid(self, form):
#        super(VoteView, self).form_valid(form)
#        #first i get the value from the form
#        getattr(self.action, "update_%s" % attr)(value, save=True)
#        
#
class EditablePoliticianView(EditableParameterView):
   pass

    

#---------------------------------------------------------------------------------

class ActionView(FormView, views_support.LoginRequiredView):
    """ Superclass to create/edit Actions """

    form_class = forms.ActionForm
    
    @method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            'title': self.request.REQUEST.get('title', ''),
            'text': self.request.REQUEST.get('text', ''),
            'tags': self.request.REQUEST.get('tags', ''),
            'in_nomine': self.request.REQUEST.get('in_nomine', ''),
            'wiki': False,
            'is_anonymous': False,
        }
    
    def get_form(self, form_class):

        #KO: form = super(ActionView, self).get_form(form_class)
        # Override default get_form() in order to pass "request" correctly
        form = form_class(self.request, **self.get_form_kwargs())
        form.hide_field('openid')
        form.hide_field('post_author_email')
        form.hide_field('post_author_username')
        form.hide_field('wiki')
        form.hide_field('ask_anonymously')
        return form

class ActionCreateView(ActionView):
    """Create a new Action.

    Firstly, a new askbot question (and thus a new Thread) is created.
    This cause a new Action to be automatically created, with the Thread 
    as a o2o field.

    Secondly, the Action relations with
        * geonames, 
        * categories,
        * politicians,
        * medias
    are set basing on the set of values reveived with the form.
    The same holds for the tags defined by the User who submitted the
    form.
    """

    template_name = "action/create.html"
    
    @transaction.commit_on_success
    def form_valid(self, form):
        """Create askbot question --> then set action relations"""

        timestamp = datetime.datetime.now()
        title = form.cleaned_data['title']
        tagnames = form.cleaned_data['tags']
        text = form.cleaned_data['text']
        in_nomine = form.cleaned_data['in_nomine']

        question = self.request.user.post_question(
            title = title,
            body_text = text,
            tags = tagnames,
            wiki = False,
            is_anonymous = False,
            timestamp = timestamp
        )

        action = question.action 

        if in_nomine[:3] == "org":
            in_nomine_pk = int(in_nomine[4:])
            action.in_nomine_org = Organization.objects.get(pk=in_nomine_pk)
            action.save()

        for m2m_attr in (
            'geoname_set', 
            'category_set',
            'politician_set',
            'media_set'
        ):
            m2m_value = form.cleaned_data.get(m2m_attr)
            if len(m2m_value) != 0:
                getattr(action, m2m_attr).add(*m2m_value)

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

class ActionUpdateView(ActionView, SingleObjectMixin):
    """Update an action

    Firstly, the question of the Thread related to the Action to update is
    edited with the data got from the validated form.
 
    Then, the Action relations with
        * geonames, 
        * categories,
        * politicians,
        * medias
    are updated basing on the set of values reveived with the form.
    The Action question tags are updated with the ones defined by the User 
    who submitted the form.
    """
    model = Action
    template_name = "action/update.html"
        
    @transaction.commit_on_success
    def form_valid(self, form):
        """Edit askbot question --> then set action relations"""

        action = self.get_object()
        
        #WAS: if action.status not in (action_const.ACTION_STATUS_DRAFT, ):
        #WAS:     return views_support.response_error(self.request, msg=exceptions.EditActionInvalidStatusException(action.status))

        self.request.user.assert_can_edit_action(action)

        question = action.question 

        title = form.cleaned_data['title']
        #theese tags will be replaced to the old ones
        tagnames = form.cleaned_data['tags']
        text = form.cleaned_data['text']

        self.request.user.edit_question(
            question = question,
            title = title,
            body_text = text,
            revision_comment = None,
            tags = tagnames,
            wiki = False, 
            edit_anonymously = False,
        )   

        for m2m_attr in (
            'geoname_set', 
            'category_set',
            'politician_set',
            'media_set'
        ):
            m2m_value = form.cleaned_data.get(m2m_attr)

            #WAS: if m2m_value is not None:
            if len(m2m_value) != 0:
                # Values can be overlapping or non overlapping
                m2m_values_old = getattr(action, m2m_attr).all()
                m2m_values_new = m2m_value

                to_add, to_remove = self.update_values(m2m_values_old, 
                    m2m_values_new
                )

                getattr(action, m2m_attr).add(*to_add)
                getattr(action, m2m_attr).remove(*to_remove)
    
        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

    def update_values(self, old_values, new_values):
        """ Get two sets of values as input and return two sets of values as output.

        This can be used when receiving a set of objects of the same tipe from a form 
        to determine, knowing the old set of values, which objects have to be
        removed, which ones have to be added and which ones have to be kept.
        
        The outputted set contain respectively the objects to add and the objects
        to remove.
        """

        to_add = []
        to_remove = []
        count = 0
        values_new_length = len(new_values)

        for obj_new in new_values:
            to_add.append(obj_new)

        for obj_old in old_values:
            #print "old %s" % obj_old.id
            for obj_new in new_values:
                #print "new %s" % obj_new.id
                if obj_old.id == obj_new.id:
                    #already present, does not need 
                    #to be added
                    to_add.remove(obj_new)
                    break
                else:
                    count = count + 1

            if values_new_length == count:
                #the old value is not present in the new set
                #of selected values
                to_remove.append(obj_old)

            count = 0
        
        return to_add, to_remove


class ActionFollowView(SingleObjectMixin, views_support.LoginRequiredView):
    """ Allow to an User to follow an Action

    A follower of an Action can receive notifications of the Action updates, 
    with respect to the Action itself and all the objects linked to it.

    A User can follow an action only if it is in a valid states. Valid states
    are:
        * ready
        * active
        * closed
        * victory
    
    This view accepts only POST requests.
    """
    model = Action
   
    def post(self, request, *args, **kwargs):

        action = self.get_object()
        user = request.user

        user.assert_can_follow_action(action)
        user.follow_action(action)
        
        return views_support.response_success(request)

class ActionUnfollowView(SingleObjectMixin, views_support.LoginRequiredView):
    """ Allow to an User to unfollow an Action

    By unfollowing an Action a User stops to receive notifications of the 
    Action updates, with respect to the Action itself and all the objects 
    linked to it.
   
    This view accepts only POST requests.
    """

    model = Action

    def post(self, request, *args, **kwargs):

        action = self.get_object()
        user = request.user
        user.assert_can_unfollow_action(action)
        user.unfollow_action(action)
        
        return views_support.response_success(request)

class ActionModerationRemoveView(FormView, SingleObjectMixin, views_support.LoginRequiredView):

    model = Action
    form_class = forms.ModeratorRemoveForm
    template_name = 'moderation/remove.html'

    @method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionModerationRemoveView, self).dispatch(request, *args, **kwargs)
 
    def get_form_kwargs(self):
        kwargs = super(ActionModerationRemoveView, self).get_form_kwargs()
        kwargs['action'] = self.get_object()
        return kwargs

    @transaction.commit_on_success
    def form_valid(self, form):

        sender = self.request.user
        action = self.get_object()
        moderator = form.cleaned_data['moderator']
        #notes = form.cleaned_data['text']

        sender.assert_can_remove_action_moderator(sender, moderator, action)

        action.moderator_set.remove(moderator)

        action_moderator_removed.send(sender=action, 
            moderator=moderator
        )

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)
