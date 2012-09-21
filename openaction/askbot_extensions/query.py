from django.db.models.query import QuerySet

class VoteQuerySet(QuerySet):

    def anonymous(self, user=None):
        """Return only anonymous votes"""

        kw = { 'is_anonymous' : True }
        if user:
            kw.update({ 'user' : user })

        return self.filter(**kw)

    def declareds(self, user=None):
        """Declared is the opposite of anonymous"""

        kw = { 'is_anonymous' : False }
        if user:
            kw.update({ 'user' : user })

        return self.filter(**kw)
