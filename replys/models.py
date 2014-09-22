from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
User = settings.AUTH_USER_MODEL
from common.models import *
from topics.models import Topic

class Reply(models.Model):
    """
    """
    creater = models.ForeignKey(User,
            related_name="topics_reply_creater",
         )
    receiver = models.ForeignKey(User,
            related_name="topics_reply_receiver",
         )
    hoster = models.ForeignKey(Topic)
    content = models.TextField(max_length=2000)
    edit_time = models.DateTimeField(auto_now=True) 
    create_time = models.DateTimeField(auto_now_add=True)

    vote_sum = models.SmallIntegerField(default=0)
    favor_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

    @property
    def anchor(self): 
        return self.address+'-'
        
    @property
    def address(self): 
        return "%s-%s-%s"%(self._meta.app_label,self._meta.model_name,self.pk)  
    
    def get_absolute_url(self):
        return self.hoster.url+'#'+self.address

    @property
    def url(self):
        return self.get_absolute_url()+'-'

    def __str__(self):
        return '%s:%s'%(self.creater, self.content[:7])

    def get_accept_mark(self,user):
        raise NotImplemented
        
    def get_vote_mark(self,user,mark_list=None):
        VOTEUP_OFF,VOTEDOWN_OFF,VOTEUP_ON,VOTEDOWN_ON=(
            'vote-up-off',
            'vote-down-off',
            'vote-up-on',
            'vote-down-on',) if mark_list is None else mark_list
        if user.is_anonymous():
            return VOTEUP_OFF,VOTEDOWN_OFF
        vote=self.vote_set.filter(creater = user).last()
        if vote is None:
            return VOTEUP_OFF,VOTEDOWN_OFF
        k=vote.value
        if k==1:
            return VOTEUP_ON,VOTEDOWN_OFF
        elif k==0:
            return VOTEUP_OFF,VOTEDOWN_OFF
        else:
            return VOTEUP_OFF,VOTEDOWN_ON 
        
    def get_favor_mark(self,user):
        if user.is_anonymous():
            return 'favor-off'#'disabled'
        if user in [c.creater for c in self.favor_set.all() if c.is_favor]:
            return 'favor-on'
        else:
            return 'favor-off'

class Comment(CommentBase):
    """
    """
    hoster = models.ForeignKey(Reply)

class Vote(VoteBase):
    """
    """
    hoster = models.ForeignKey(Reply)

class Favor(FavorBase):
    """
    """
    hoster = models.ForeignKey(Reply)
