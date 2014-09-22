from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
User = settings.AUTH_USER_MODEL
from common.models import TagBase, VoteBase, FavorBase,CommentBase


class Tag(TagBase): 
    """
    """
    pass
 
class Topic(models.Model):
    """
    """
    creater = models.ForeignKey(User)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=2000)  
    create_time = models.DateTimeField(auto_now_add=True)
    edit_time = models.DateTimeField(auto_now=True)
    accept_pk = models.SmallIntegerField(default=0)

    tags = models.ManyToManyField(Tag, related_name='topics') 

    vote_sum = models.SmallIntegerField(default=0)
    favor_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    def get_absolute_url(self):
        return reverse('topics:TopicDetail',args=(self.pk,))
        
    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def address(self): 
        return "%s-%s-%s"%(self._meta.app_label,self._meta.model_name,self.pk)   

    def __str__(self):
        return '%s:%s'%(self.creater,self.title[:15])

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
    hoster = models.ForeignKey(Topic)

class Vote(VoteBase):
    """
    """
    hoster = models.ForeignKey(Topic)

class Favor(FavorBase):
    """
    """
    hoster = models.ForeignKey(Topic)