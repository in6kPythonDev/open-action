"""Some commodities extensions for Askbot models.

"""

from django.db import models

from askbot.models import Thread

from lib.djangolib import ModelExtender


#--------------------------------------------------------------------------------

class ThreadExtension(ModelExtender):

    ext_prefix = '_askbot_ext_'

    @property
    def _askbot_ext_question(self):
        return self._question_post()


Thread.add_to_class('thread_ext_noattr', ThreadExtension())

#--------------------------------------------------------------------------------

class PostExtension(ModelExtender):
    pass

    
#TODO TOTHINK if we could enlarge even the summary field...

#--------------------------------------------------------------------------------

#TODO: place can be blank/null at creation time?
#TODO TOTHINK User.add_to_class("place", models.CharField(max_length=512))

#--------------------------------------------------------------------------------

class VoteExtension(ModelExtender):

    ext_prefix = '_askbot_ext_'

    def _askbot_ext_save(self, *args, **kw):

        orig_save = self._orig_method
        if self.referral:
            if self.referral == self.user:
                # TODO: specific exception
                raise PermissionDenied("Cannot be referred by yourself")

        orig_save(self, *args, **kw)
        


Vote.add_to_class('referral', 
    models.ForeignKey(User, null=True, blank=True)
)
