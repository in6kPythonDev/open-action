from django.db import models

from askbot.models import Thread
from action import const

class Action(models.Model):

    # Extending Askbot model!
    thread = models.OneToOneField(Thread)

    victory = models.BooleanField(default=False)

    threshold = models.PositiveIntegerField(blank=True, null=True)

    # Status can be 
    # CREATED, DRAFT, CANCELED DRAFT, ACTIVE, CLOSED, VICTORY
    @property
    def status(self):

        if self.victory:
            status = const.ACTION_STATUS['victory']
        elif self.thread.closed:
            status = const.ACTION_STATUS['closed']
        elif self.question.deleted:
            status = const.ACTION_STATUS['deleted']
        elif self.score == 0:
            # cannot be voted until all fields are set
            # so the Action goes into "draft" status
            status = const.ACTION_STATUS['created']
        elif not self.threshold or self.score < self.threshold:
            status = const.ACTION_STATUS['draft']
        elif self.score >= self.threshold:
            status = const.ACTION_STATUS['active']
        return status

    @property
    def question(self):
        #TODO: should be moved in askbot Thread class
        return self.thread._question_post()
        

    @property
    def title(self):
        status = ""
        if self.status != const.ACTION_STATUS['active']:
            status = u" [%s]" % self.status
        return u"%s%s" % (self.thread.title, status)
    

    @property
    def description(self):
        """Description is a quite short summary of the action"""

        # TODO TOTHINK 
        # Askbot summary is 300 chars long, we should enlarge it...
        return self.question.summary
    
    @property
    def score(self):
        return self.question.score

    @property
    def content(self):
        return self.question.text

    @property
    def votes(self):
        return self.question.votes

    @property
    def voters(self):
        return self.votes.values('user__username').order_by('-voted_at') 

    @property
    def comments(self):
        return self.question.comments.all()


class GeoName(models.Model):

    GEO_CHOICES = (
        ('state', 'Stato'),
        ('province', 'Provincia'),
        #TODO: Matteo
    )

    name = models.CharField(max_length=1024)
    kind = models.CharField(max_length=32, choices=GEO_CHOICES)

    # Modifier for threshold computation
    threshold_factor = models.FloatField(default=1)



