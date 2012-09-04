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

from lib import views_support

import logging

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

class VoteView(SingleObjectMixin, LoginRequiredView):
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
            return views_support.response_error(request, msg=VoteActionInvalidStatusException(action.status))

        action.vote_add(request.user)
        return views_support.response_success(request)

class CommentVoteView(VoteView):
    """Add a vote to an Action comment."""
    
    model = Post

    def post(self, request, *args, **kwargs):
        pass 

#---------------------------------------------------------------------------------

class CommentView(FormView, SingleObjectMixin, LoginRequiredView):
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
        action.comment_add(form.cleaned_data['text'], self.request.user)
        return views_support.response_success(self.request)


class BlogpostCommentView(CommentView):
    """ Add a comment to an action blogpost"""

    #to get the object
    model = Post
    template_name = 'comment/add.html'
    form_class = forms.BlogpostCommentForm

    def form_valid(self, form):
        """ Redirect to get_success_url(). Must return an HttpResponse."""
        action = self.get_object().thread.action
        action.blogpost_comment_add(self.get_object(),
            form.cleaned_data['text'], 
            self.request.user
        )
        return views_support.response_success(self.request)

#---------------------------------------------------------------------------------

class BlogpostView(FormView, SingleObjectMixin, LoginRequiredView):
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

class ActionCreateView(FormView, LoginRequiredView):
    """Create a new action

    """

    form_class = forms.ActionForm
    template_name = "action/create.html"
    
    @method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionCreateView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        form = super(ActionCreateView, self).get_form(form_class)
        form.hide_field('openid')
        form.hide_field('post_author_email')
        form.hide_field('post_author_username')
        return form
        
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

        for m2m_attr in ('geoname_set', 'category_set'):
            m2m_value = form.cleaned_data.get(m2m_attr)
            if m2m_value:
                getattr(action, m2m_attr).add(*m2m_value)

        return super(ActionCreateView, self).form_valid(form)

    def get_initial(self):
        return {
            'title': self.request.REQUEST.get('title', ''),
            'text': self.request.REQUEST.get('text', ''),
            'tags': self.request.REQUEST.get('tags', ''),
            'wiki': False,
            'is_anonymous': False,
        }

