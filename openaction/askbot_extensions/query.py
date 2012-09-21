from django.db.models.query import QuerySet

class VoteQuerySet(QuerySet):

    def anonymous(self, user=None, action=None):
        """Return only anonymous votes"""

        kw = { 'is_anonymous' : True }
        if user:
            kw.update({ 'user' : user })
        if action:
            kw.update({ 'action' : action })

        return self.filter(**kw)

    def declareds(self, user=None, action=None):
        """Declared is the opposite of anonymous"""

        kw = { 'is_anonymous' : False }
        if user:
            kw.update({ 'user' : user })
        if action:
            kw.update({ 'action' : action })

        return self.filter(**kw)
