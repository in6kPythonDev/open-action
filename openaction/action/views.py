from django.views.generic.detail import DetailView,SingleObjectMixin
from django.views.generic.edit import UpdateView
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django.utils.decorators import method_decorator

from askbot.models import Post
from askbot.models.repute import Vote
from action.models import Action
from action import const as action_const

from action.exceptions import ActionInvalidStatusException
from lib import views_support

import logging

log = logging.getLogger("openaction")

#DELETE just for testing
from django.http import HttpResponse

#DELETE just for testing
def test_post_view(request):
    html = "<html><head><title>VOTA l'AZIONE!</title></head> \
        <body><form method=\"post\" action=\"question/1/vote/\"> \
        <input type=\"submit\" value=\"submit\" /></form></body></html>"
    return HttpResponse(html)
    
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

class VoteView(View, SingleObjectMixin):
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(VoteView, self).dispatch(*args, **kwargs)

class ActionVoteView(VoteView):
    """Add a vote to an Action."""

    model = Action

    def post(self, request, *args, **kwargs):

        try:
            action = self.get_object()
            log.debug("%s:user %s voting action %s" % (
                self.__class__.__name__.lower(),
                request.user, action
            ))
            
            #QUESTION: should an action which reached 'victory' status
            # still be votable?
            if action.status not in (
                action_const.ACTION_STATUS_READY, 
                action_const.ACTION_STATUS_ACTIVE
            ):
                return views_support.response_error(request, msg=ActionInvalidStatusException())

            action.vote_add(request.user)
            return views_support.response_success(request)
                
        except Exception as e:
            log.debug("Exception raised %s" % e)
            return views_support.response_error(request, msg=e)
        
class CommentVoteView(VoteView):
    """Add a vote to an Action comment."""

    model = Post
    
    def post(self, request, *args, **kwargs):
        pass 
        # comment = get_object()
        # controlla post_type
        #note: vote = request.user.upvote(comment) 

#---------------------------------------------------------------------------------

    class CommentView(View, SingleObjectMixin):
        """ Add a comment to a post"""
        pass

    class ActionCommentView(CommentView):
        """ Add a comment to an action"""
        pass

    class 

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

#@decorators.check_spam('text')
#def ask(request):#view used to ask a new question
#    """a view to ask a new question
#    gives space for q title, body, tags and checkbox for to post as wiki
#
#    user can start posting a question anonymously but then
#    must login/register in order for the question go be shown
#    """
#    form = forms.AskForm(request.REQUEST)
#    if request.method == 'POST':
#        if form.is_valid():
#            timestamp = datetime.datetime.now()
#            title = form.cleaned_data['title']
#            wiki = form.cleaned_data['wiki']
#            tagnames = form.cleaned_data['tags']
#            text = form.cleaned_data['text']
#            ask_anonymously = form.cleaned_data['ask_anonymously']
#
#            if request.user.is_authenticated():
#                
#                user = form.get_post_user(request.user)
#                try:
#                    question = user.post_question(
#                        title = title,
#                        body_text = text,
#                        tags = tagnames,
#                        wiki = wiki,
#                        is_anonymous = ask_anonymously,
#                        timestamp = timestamp
#                    )
#                    return HttpResponseRedirect(question.get_absolute_url())
#                except exceptions.PermissionDenied, e:
#                    request.user.message_set.create(message = unicode(e))
#                    return HttpResponseRedirect(reverse('index'))
#
#            else:
#                request.session.flush()
#                session_key = request.session.session_key
#                summary = strip_tags(text)[:120]
#                models.AnonymousQuestion.objects.create(
#                    session_key = session_key,
#                    title       = title,
#                    tagnames = tagnames,
#                    wiki = wiki,
#                    is_anonymous = ask_anonymously,
#                    text = text,
#                    summary = summary,
#                    added_at = timestamp,
#                    ip_addr = request.META['REMOTE_ADDR'],
#                )
#                return HttpResponseRedirect(url_utils.get_login_url())
#
#    if request.method == 'GET':
#        form = forms.AskForm()
#
#    form.initial = {
#        'title': request.REQUEST.get('title', ''),
#        'text': request.REQUEST.get('text', ''),
#        'tags': request.REQUEST.get('tags', ''),
#        'wiki': request.REQUEST.get('wiki', False),
#        'is_anonymous': request.REQUEST.get('is_anonymous', False),
#    }
#
#    data = {
#        'active_tab': 'ask',
#        'page_class': 'ask-page',
#        'form' : form,
#        'mandatory_tags': models.tag.get_mandatory_tags(),
#        'email_validation_faq_url':reverse('faq') + '#validate',
#    }
#    return render_into_skin('ask.html', data, request)
#
