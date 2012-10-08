
from django.db import models
from action.query import ActionQuerySet

class ActionManager(models.Manager):

    def get_query_set(self):
        return ActionQuerySet(self.model)

    def actives(self):
        return self.get_query_set().actives()
