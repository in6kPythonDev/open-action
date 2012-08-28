from django.views.generic.detail import DetailView

from askbot.models import Post
from action.models import Action

class ActionDetailView(DetailView):

    model = Action
    context_object_name="action" 
    template_name="action_detail.html"

    def get_object(self):
        self.instance = super(ActionDetailView, self).get_object()
        # needs to do something here...?
        # POSSIBLE TODO: parse token and increment counter "action suggested by user"
        return self.instance

    def get_context_data(self, **kwargs):
        context = super(ActionDetailView, self).get_context_data(**kwargs)
        # needs to do something here...?
        # a set
        #attrs = ('',
        #    '',
        #)
        return context

#---------------------------------------------------------------------------------

class VoteView(View, SingleObjectMixin):
    """Aumenta di 1 il voto 

    * accessibile solo tramite POST
    * recupera la action in "def get_object(self)"
    * aggiungere un voto ad una action
    * aggiungere un voto solo se in uno stato ammissibile
    * l'utente sia autenticato
   
    SUCCESSIVAMENTE (ma non lo fare)
    * prenderemo via url HTTP il parametro "token" per capire
      da chi è stato inviato il link
    """

    model = Post

class ActionVoteView(VoteView):
    """Aggiunge un voto su una action."""
    pass

class CommentVoteView(VoteView):
    """Aggiunge un voto su un commento."""
    pass

#---------------------------------------------------------------------------------

class EditableParameterView(UpdateView):
    """Consente di editare un attributo di un modello.

    * accessibile solo tramite POST
    * recupera l'istanza del modello Action
    * fa getattr(instance, "update_%s" % <attr_name>)(value, save=True) 
    * dove value è request.POST["value"]
    per testare:
    <form method="post" action="/action/1/edit/title">
        <input type="text" value="nuovo titolo" />
        <input type="submit" value="submit" />
    </form>

    * Devi definire in action i metodi update_xxxx (tipo update_title)
    che prendono come parametro il valore e un flag "save" per capire se devono
    anche salvarlo istantaneamente.
    """
    
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
