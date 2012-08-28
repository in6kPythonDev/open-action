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
