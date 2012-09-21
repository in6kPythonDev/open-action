
from askbot.models import repute
from askbot_extensions.query import VoteQuerySet

class VoteManager(repute.VoteManager):

    def get_query_set(self):
        return VoteQuerySet(self.model)

    def anonymous(self, user=None, action=None):
        return self.get_query_set().anonymous(user=user, action=action)

    def declareds(self, user=None, action=None):
        """Declared is the opposite of anonymous"""
        return self.get_query_set().declareds(user=user, action=action)

    def referred_by(self, referral):
        """Get votes referred by the referral user"""
        return self.get_query_set().referred_by(referral=referral)
