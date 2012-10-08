
from django.db.models.query import QuerySet

from action import const as act_consts

class ActionQuerySet(QuerySet):

    def actives(self):
        #WARNING: can be slow!
        return [action for action in self 
            if action.status == act_consts.ACTION_STATUS_ACTIVE
        ]

