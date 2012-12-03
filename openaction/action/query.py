
from django.db.models.query import QuerySet

from action import const as act_consts

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

