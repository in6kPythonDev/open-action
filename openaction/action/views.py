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
from action.models import Action, Geoname, Politician, Media
from action import const as action_const
from action import forms
from action.signals import action_moderator_removed
from askbot_extensions import utils as askbot_extensions_utils
from organization.models import Organization
from external_resource.models import ExternalResource
from external_resource import utils
from ajax_select import get_lookup
from action.lookups import GeonameDict

from lib import views_support

import exceptions
import logging, datetime

log = logging.getLogger(settings.PROJECT_NAME)


MAP_MODEL_SET_TO_CHANNEL = {
    'geoname_set' : 'geonamechannel', 
    'politician_set' : 'politicianchannel',
    'media_set' : 'TODO',
}

#NOTE: 'resource' here is meant as a pool of data. Are there better terms?
MAP_RESOURCE_TO_CHANNEL = {
    'cityrep' : 'cityrepchannel'
}

#geographical places
GEO_LOCALIZATIONS = {
    'comune' : ['consiglio','giunta',],
    'provincia' : ['consiglio','giunta',],
    'regione' : ['consiglio','giunta',],
}
INSTITUTIONS = {
    'senato' : ['representatives',],
    'europarl' : ['representatives',],
    'camera' : ['representatives',],
}

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
    """Base class to add a vote to an action

    Include facility method to check referral token variable in url
    and return referral user if found.
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
    
    #@method_decorator(askbot_decorators.check_spam('text'))
    #def dispatch(self, request, *args, **kwargs):
    #    return super(ActionView, self).dispatch(request, *args, **kwargs)

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
        #using the askbot logic to hide our fields
        form.hide_field('threshold')
        return form
        
    def get_m2m_values(self, 
            m2m_attr, 
            m2m_value, 
            model,
            **kwargs
    ):
        """ Here we have to check if there are ExternalResource
        objects with pk equal to the provided ids.
        If there are ids that do not match with any ExternalResource
        object pk, than create them. 
        If the ExternalResource which pks match with some ids was
        created too time ago, then check the openpolis Json to see
        if there had been some changes.
        
        Finally check if there are Geoname objects linked to the found
        ExternalResource objects. If not, create them.
        
        """
        m2m_values = []
        ext_res = []
        new_ext_res = []

        lookup = get_lookup(MAP_MODEL_SET_TO_CHANNEL[m2m_attr])
        #print("\nm2m_value: %s" % m2m_value)
        m2m_value = lookup.get_objects(m2m_value)
        #print("\nJSON_DATA: %s\n" % m2m_value)
        for json_datum in m2m_value:
            try:
                #print("\ndatum: %s" % json_datum)
                _id = json_datum['%s%s%s' % (
                    kwargs.get('id_prefix',''),
                    'id',
                    kwargs.get('id_suffix','')
                    )
                ]
                e_r = ExternalResource.objects.get(pk=_id)
                if (datetime.datetime.now() - e_r.last_get_on).days < settings.MAX_TIME_ELAPSED:
                    ext_res.append(e_r)
                else:
                    #WAS: datum = lookup.get_objects([_id])
                    datum = lookup.get_objects([_id])[0]
                    self.update_external_resource(e_r, datum)
                    ext_res.append(e_r)
            except ExternalResource.DoesNotExist as e:
                #array of ExternalResource objects to create
                new_ext_res.append(_id)

        for _id in new_ext_res:
            #Here i should GET json data and create object
            #was: datum = lookup.get_objects([_id])
            datum = lookup.get_objects([_id])[0]
            #print("\ndatum: %s" % datum)
            #TODO: check ex_res_tupe. It changes depending to model
            e_r = ExternalResource.objects.create(
                backend_name = lookup.get_backend_name(),
                ext_res_id = _id,
                #WAS: ext_res_type = datum['location_type']['name'],
                ext_res_type = datum[
                    kwargs['ext_res_type']['type']][
                    kwargs['ext_res_type']['name']],
                first_get_on = datetime.datetime.now(),
                last_get_on = datetime.datetime.now()
            )
            e_r.save()
            ext_res.append(e_r)

        for e_r in ext_res:
            try:
                instance = model.objects.get(external_resource=e_r)
                #WAS: m2m_values.append(instance.pk)
                m2m_values.append(instance)
            except model.DoesNotExist as e:

                instance = self.create_object(model,
                    e_r,
                    lookup,
                    **kwargs
                )
                #WAS: m2m_values.append(instance.pk)
                m2m_values.append(instance)

        return m2m_values

    def create_object(self,
        model,
        e_r,
        lookup,
        **kwargs
    ):
        """ Create object starting from json data """
        if model == Geoname:
            #Here i should GET json data to create obj
            datum = lookup.get_objects([e_r.ext_res_id])[0]
            if kwargs['ext_res_type']:
                kind=datum[
                    kwargs['ext_res_type']['type']][
                    kwargs['ext_res_type']['name']]
            elif kwargs['politician_data']:
                #TODO: politician data
                kind=""
            else:
                raise exceptions.ProgrammingError

            instance = model(
                #WAS: name=datum[kwargs['ext_res_name']],
                name=datum[kwargs['name']],
                #WAS: kind=datum['location_type']['name'],
                kind=kind,
                external_resource=e_r
            )
            instance.save()
        elif model == Politician:
            #GET json data to create politician
            datum = [elem for elem in kwargs['politicians_ids'] 
                if elem['politician_id'] == e_r.ext_res_id][0]
            instance = model(
                first_name=datum['first_name'],
                last_name=datum['last_name'],
                birth_date=datum['birth_date'],
                # place cherge here, in the model too 
                external_resource=e_r
            )
            instance.save()
        elif model == Media:
            #TODO
            instance = None

        return instance

    def update_external_resource(self, e_r, json_datum):
        """ Update external resource with the data get from the json """
        #TODO: change implementation? problably....
        if e_r.ext_res_id != json_datum['id']:
            e_r.ext_res_id = json_datum['id']
        if e_r.ext_res_type != json_datum['location_type']['name']:
            e_r.ext_res_id = json_datum['location_type']['name']
        e_r.last_get_on = datetime.datetime.now()
        
        e_r.save()

        return

    def check_threshold(self, 
        cityreps_ids,
        politicians_ids,
        lookup,
        total_threshold,
        **kwargs
    ):
        """ Get information needed to compute the chosen politicians 
        threshold deltas.

        Search politicians ids in each cityrep connected to the locations
        until all the data needed is collected.

        The json is strcutured like this:

            "city_representatives" {
                <geographic location>:{
                    "consiglio":[]
                    "giunta":[]
                }
                ...
                <institution>:{
                    "constituency":""
                    "representatives":[]
                }
                ...
            }
                 
        """
        
        politicians_data = []
        computed_threshold = 0

        for cityreps_id in cityreps_ids:
            if len(politicians_ids) == 0:
                break
            cityrep = lookup.get_objects([cityreps_id])[0]['city_representatives']

            for geo_loc in GEO_LOCALIZATIONS.keys():
                if len(politicians_ids) == 0:
                    break
                politicians_ids_to_check = []
                for elem in politicians_ids:
                    politicians_ids_to_check.append(elem)
                #iterating over geo localizations
                for politician_id in politicians_ids_to_check:
                    politician_data, threshold_delta = self.check_politician(
                        cityrep[geo_loc], 
                        politician_id,
                        politicians_ids,
                        geo_loc=geo_loc
                    )
                    if politicians_data:
                        politicians_data.append(politician_data)
                    computed_threshold = computed_threshold + threshold_delta

            for institution in INSTITUTIONS.keys():
                if len(politicians_ids) == 0:
                    break
                #iterating over inatitutions
                politicians_ids_to_check = []
                for elem in politicians_ids: 
                    politicians_ids_to_check.append(elem)
                for politician_id in politicians_ids_to_check:
                    print("\ninstitution: %s" % institution)
                    print("\nid: %s" % politician_id)
                    print("\n\nids: %s" % politicians_ids)
                    politician_data, threshold_delta = self.check_politician(
                        cityrep[institution], 
                        politician_id,
                        politicians_ids,
                        institution=institution
                    )
                    if politicians_data:
                        politicians_data.append(politician_data)
                    computed_threshold = computed_threshold + threshold_delta

            if computed_threshold != total_threshold:
                #TODO: define exception
                raise Exception
            
            return politicians_data

    def check_politician(self, 
        politicians, 
        politician_id, 
        politicians_ids,
        **kwargs
        ):
        """ Check whether a certain politician is contained into a given set 
        of politicians 

        * politicians: json data 
        * politician_id: id of the politician to check
        * politician_ids: set of politicians
        """ 
        
        politician_data = []

        if kwargs.get('geo_loc'):
            geo_loc = kwargs['geo_loc']
            #print("\n%s" % GEO_LOCALIZATIONS.get(geo_loc)[0])
            #print("\n%s" % politicians)
            #print("\n%s" % politicians[GEO_LOCALIZATIONS.get(geo_loc)[0]])
            elements = politicians[GEO_LOCALIZATIONS.get(geo_loc)[0]].extend(
                politicians[GEO_LOCALIZATIONS.get(geo_loc)[1]]
            )
            if elements is None:
                elements = []

            for elem in elements:
                if elem['politician_id'] == politician_id:
                    politician_data = elem
                    break
            
            if politician_data:
                politicians_ids.remove(politician_id)
                #TODO: Computing threshold delta
                threshold_delta = 0
                return politician_data, threshold_delta

        elif kwargs.get('institution'):
            institution = kwargs['institution']
            for elem in politicians[INSTITUTIONS.get(institution)[0]]:
                if elem['politician_id'] == politician_id:
                    politician_data = elem
                    break

            if politician_data:
                politicians_ids.remove(politician_id)
                #TODO: Computing threshold delta
                threshold_delta = 0
                return politician_data, threshold_delta

        return politician_data,0
                
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
        total_threshold = int(form.cleaned_data['threshold'])

        question = self.request.user.post_question(
            title = title,
            body_text = text,
            tags = tagnames,
            wiki = False,
            is_anonymous = False,
            timestamp = timestamp
        )

        action = question.action 

        # check if this action is created by an organization
        if in_nomine[:3] == "org":
            in_nomine_pk = int(in_nomine[4:])
            log.debug("IN_NOMINE %s _PK %s" % (in_nomine[:3], in_nomine[4:]))
            action.in_nomine_org = Organization.objects.get(pk=in_nomine_pk)
            action.save()

        for m2m_attr in (
            'category_set',
        ):
            m2m_value = form.cleaned_data.get(m2m_attr)

            if len(m2m_value) != 0:
                getattr(action, m2m_attr).add(*m2m_value)

        for m2m_attr in (
            'geoname_set', 
            'politician_set',
            'media_set'
        ):
            #Theese attributes should contain Json data
            m2m_value = form.cleaned_data.get(m2m_attr)
            print "\n%s\n"% m2m_value
            if m2m_attr[:-4] == 'geoname':
                model = Geoname
                kwargs = {}
                kwargs['ext_res_type'] = {
                    'type' : 'location_type',
                    'name' : 'name'
                }
                kwargs['name'] = 'name'
            elif m2m_attr[:-4] == 'politician':
                model = Politician
                kwargs = {}
                #GET cityreps from locations ids
                cityreps_ids = form.cleaned_data.get('geoname_set')
                # here we check that the threshold arrived is equal to
                # the the sum of the thrershold delta of all the politicians
                # the metho dwill raise exceptions if necessary
                #kwargs['charge_ids'] = self.get_politicians_charge_ids(
                #    cityreps_ids,
                #    m2m_value,
                #    get_lookup(MAP_MODEL_SET_TO_CHANNEL['cityrep'])
                #)
                if type(m2m_value) != list:
                    m2m_value = [int(elem) for elem in m2m_value.strip('|').split('|')]
                kwargs['politicians_data'] = self.check_threshold(
                    cityreps_ids,
                    m2m_value,
                    get_lookup(MAP_RESOURCE_TO_CHANNEL['cityrep']),
                    total_threshold
                )
                kwargs['id_prefix'] = 'content_'
            elif m2m_attr[:-4] == 'media':
                kwargs = {}
                model = Media

            if len(m2m_value) != 0:

                m2m_values = self.get_m2m_values(
                    m2m_attr,
                    m2m_value,
                    model,
                    #ext_res_type={
                    #    'type' : 'location_type',
                    #    'name' : 'name'
                    #},
                    **kwargs
                )

                getattr(action, m2m_attr).add(*m2m_values)

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
            'category_set',
        ):
            m2m_value = form.cleaned_data.get(m2m_attr)

            if len(m2m_value) != 0:
                m2m_values_old = getattr(action, m2m_attr).all()
                to_add, to_remove = self.update_values(m2m_values_old, 
                    m2m_values_new
                )

                getattr(action, m2m_attr).add(*to_add)
                getattr(action, m2m_attr).remove(*to_remove)

        for m2m_attr in (
            'geoname_set', 
            'politician_set',
            'media_set'
        ):
            #Theese attributes should contain Json data
            m2m_value = form.cleaned_data.get(m2m_attr)
            if m2m_attr[:-4] == 'geoname':
                model = Geoname
            elif m2m_attr[:-4] == 'politician':
                model = Politician
                kwargs['cityrep']
            elif m2m_attr[:-4] == 'media':
                model = Media

            if len(m2m_value) != 0:
                """ Here we have to check if there are ExternalResource
                objects with pk equal to the provided ids.
                If there are ids that do not match with any ExternalResource
                object pk, than create them. 
                If the ExternalResource which pks match with some ids was
                created too time ago, then check the openpolis Json to see
                if there had been some changes.
                
                Finally check if there are Geoname objects linked to the found
                ExternalResource objects. If not, create them.
                
                """
                # Values can be overlapping or non overlapping
                m2m_values_old = getattr(action, m2m_attr).all()

                m2m_values_new = self.get_m2m_values(
                    m2m_attr,
                    m2m_value,
                    model,
                    #ext_res_name='name',
                    ext_res_type={
                        'type' : 'location_type',
                        'name' : 'name'
                    }
                )

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
    """ Allow to the Action owner to remove an Action moderator.

    The ex-moderator is notified of this and he can send a message to 
    the Action owner asking for the reasons behind his removal. 

    """ 

    model = Action
    form_class = forms.ModeratorRemoveForm
    template_name = 'moderation/remove.html'

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

        sender.assert_can_remove_action_moderator(
            moderator, 
            action
        )

        action.moderator_set.remove(moderator)

        action_moderator_removed.send(sender=action, 
            moderator=moderator
        )

        success_url = action.get_absolute_url()
        return views_support.response_redirect(self.request, success_url)
