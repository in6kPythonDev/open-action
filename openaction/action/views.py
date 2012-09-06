from django.views.generic.detail import DetailView,SingleObjectMixin
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic import View
from django.contrib.auth.decorators import login_required
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
import exceptions

from lib import views_support

import logging, datetime

log = logging.getLogger(settings.PROJECT_NAME)


class ActionDetailView(DetailView):

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
      
    This means that the Action score will be incremented by 1
    and that a new vote will be added to the Action question votes
    * accessibile solo tramite POST
    * recupera la action in "def get_object(self)" v
    * aggiungere un voto ad una action v
    * aggiungere un voto solo se in uno stato ammissibile v
    * l'utente sia autenticato v
   
    SUCCESSIVAMENTE (ma non lo fare)
    * prenderemo via url HTTP il parametro "token" per capire
      da chi e' stato inviato il link
    """

class ActionVoteView(VoteView):
    """Add a vote to an Action."""

    model = Action

    def post(self, request, *args, **kwargs):
        action = self.get_object()
        
        #QUESTION: should an action which reached 'victory' status
        # still be votable?
        if action.status not in (
            action_const.ACTION_STATUS_READY, 
            action_const.ACTION_STATUS_ACTIVE
        ):
            return views_support.response_error(request, msg=exceptions.VoteActionInvalidStatusException(action.status))

        #have to catch the exception raised from the presave signal
        try:
            action.vote_add(request.user)
        except exceptions.UserCannotVoteTwice as e:
            return views_support.response_error(self.request, msg=e)
        return views_support.response_success(request)

class CommentVoteView(VoteView):
    """Add a vote to an Action comment."""
    
    model = Post

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        user = request.user
        
        vote = user.upvote(comment)
        referral =  kwargs.pop('referral',None)
        
        if vote:
            # Add referral
            vote.referral = referral 
            vote.save()

            log.debug("Vote added for user %s on comment %s with referral %s" % (
                user, comment, referral
            ))
        else:
            log.debug("Vote NOT added for user %s on comment %s with referral %s" % (
                user, comment, referral
            ))
            try:
                assert comment.votes.get(user=user)
            except Post.DoesNotExist as e:
                return views_support.response_error(request, msg=exceptions.UserCannotVote(user, comment))
            else:
                return views_support.response_error(request, msg=exceptions.UserCannotVoteTwice(user, comment))
        return views_support.response_success(request) 

#---------------------------------------------------------------------------------

class CommentView(FormView, SingleObjectMixin, views_support.LoginRequiredView):
    """ Add a comment to a post"""
    
class ActionCommentView(CommentView):
    """ Add a comment to an action"""

    #to get the object
    model = Action
    template_name = 'comment/add.html'
    form_class = forms.ActionCommentForm

    def form_valid(self, form):
        """ Redirect to get_success_url(). Must return an HttpResponse."""
        action = self.get_object()
        #have to catch the exception raised from the presave signal
        try:
            action.comment_add(form.cleaned_data['text'], self.request.user)
        except exceptions.CommentActionInvalidStatusException as e:
            return views_support.response_error(self.request, msg=e)
        return views_support.response_success(self.request)


class BlogpostCommentView(CommentView):
    """ Add a comment to an action blogpost"""

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

    model = Action
    form_class = forms.ActionBlogpostForm
    template_name = 'blogpost/add.html'
 
    def form_valid(self, form):

        action = self.get_object()
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
#        action = self.post.thread.action
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
            'wiki': False,
            'is_anonymous': False,
        }
    
    def get_form(self, form_class):
        form = super(ActionView, self).get_form(form_class)
        form.hide_field('openid')
        form.hide_field('post_author_email')
        form.hide_field('post_author_username')
        return form

class ActionCreateView(ActionView):
    """Create a new action

    """

    template_name = "action/create.html"
    
    @transaction.commit_on_success
    def form_valid(self, form):
        """Create askbot question --> then set action relations"""

        timestamp = datetime.datetime.now()
        title = form.cleaned_data['title']
        tagnames = form.cleaned_data['tags']
        text = form.cleaned_data['text']

        question = self.request.user.post_question(
            title = title,
            body_text = text,
            tags = tagnames,
            wiki = False,
            is_anonymous = False,
            timestamp = timestamp
        )

        action = question.thread.action 

        for m2m_attr in (
            'geoname_set', 
            'category_set',
            'politician_set',
            'media_set'
        ):
            m2m_value = form.cleaned_data.get(m2m_attr)
            if m2m_value:
                getattr(action, m2m_attr).add(*m2m_value)

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

class ActionUpdateView(ActionView, SingleObjectMixin):
    """Update an action

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
            #ERROR TODO Matteo: if m2m_value:
            #ERROR TODO Matteo:     getattr(action, m2m_attr).add(*m2m_value)

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)

