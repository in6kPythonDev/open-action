
from django.db import models
from action.query import ActionQuerySet

class ActionManager(models.Manager):

    def get_query_set(self):
        return ActionQuerySet(self.model)

    def actives(self):
        return self.get_query_set().actives()

    def by_categories(self, *categories):
        return self.get_query_set().by_categories(*categories)

    def by_geonames(self, *geonames):
        return self.get_query_set().by_geonames(*geonames)

    def by_politicians(self, *politicians):
        return self.get_query_set().by_politicians(*politicians)
