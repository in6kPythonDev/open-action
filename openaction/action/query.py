
from django.db.models.query import QuerySet

from action import const as act_consts

import datetime

class ActionQuerySet(QuerySet):

    def actives(self):
        #WARNING: can be slow!
        return [action for action in self 
            if action.status == act_consts.ACTION_STATUS_ACTIVE
        ]

    def by_categories(self, *categories):
        return self.filter(category_set__in=categories)

    def by_geonames(self, *geonames):
        return self.filter(geoname_set__in=geonames)

    def by_politicians(self, *politicians):
        return self.filter(politician_set__in=politicians)

    def sort_by_hot(self, days):
        """ The most voted in the last period of time """
        delta = datetime.timedelta(int(days))
        return sorted(
            self.all(),key=lambda action: action.votes_since_date(delta)
        ) 

    def sort_by_popularity(self):
        """ The most voted of ever """
        return sorted(self.all(), key=lambda action: action.votes.count())

    def sort_by_date(self):
        """ The most recent """
        return self.order_by('-thread__added_at')

