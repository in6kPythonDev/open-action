
from askbot.models import repute
from askbot_extensions.query import VoteQuerySet

class VoteManager(repute.VoteManager):

    def get_query_set(self):
        return VoteQuerySet(self.model)

    def anonymous(self, user=None):
        return self.get_query_set().anonymous(user=user)

    def declareds(self, user=None):
        """Declared is the opposite of anonymous"""
        return self.get_query_set().declareds(user=user)
