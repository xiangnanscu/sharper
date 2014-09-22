from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from .manager import CommonManager

__all__ = ['FavorBase', 'CommentBase', 'VoteBase', 'TagBase',]

class ActionBase(models.Model):
    """
    """
    class Meta:
        abstract = True

    objects = CommonManager()

    creater = models.ForeignKey(User,
            related_name="%(app_label)s_%(class)s_creater",
         )
    receiver = models.ForeignKey(User,
            related_name="%(app_label)s_%(class)s_receiver",
         )
    create_time = models.DateTimeField(auto_now_add=True)

class VoteBase(ActionBase):
    """
    """
    VOTE_CHOICES = ((1, '顶'),(-1, '踩'),(0, '无'),)

    class Meta:
        abstract = True
        unique_together = ('creater', 'hoster')

    value = models.PositiveSmallIntegerField(choices=VOTE_CHOICES,default=0,)

    def __str__(self):
        return '%s:%s'%(self.creater, self.value)

class CommentBase(ActionBase):
    """
    """
    class Meta:
        abstract = True
    content = models.TextField(max_length=800)

    def __str__(self):
        return '%s:%s'%(self.creater, self.content[:7])

    @property
    def anchor(self): 
        return self.address+'-'

    @property
    def address(self): 
        return "%s-%s-%s"%(self._meta.app_label,self._meta.model_name,self.pk) 

    def get_absolute_url(self):
        return self.hoster.get_absolute_url().split('#')[0]+'#'+self.address

    @property
    def url(self):
        return self.get_absolute_url()+'-'
        
class FavorBase(models.Model):
    """
    """
    class Meta:
        abstract = True
        unique_together = ('creater', 'hoster')
    creater = models.ForeignKey(User,
            related_name="%(app_label)s_%(class)s_creater",
         )
    is_favor = models.BooleanField(default=False)
    edit_time = models.DateTimeField(auto_now=True)

class TagBase(models.Model):
    """
    """
    class Meta:
        abstract = True
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=200,default="默认标签描述") 

    def __str__(self):
        return self.name

class TagActionBase(models.Model):
    """
    """
    class Meta:
        abstract = True
    creater = models.ForeignKey(User,
            related_name="%(app_label)s_%(class)s_creater",
         )
    create_time = models.DateTimeField(auto_now_add=True)

class Flag(models.Model):
    """
    """
    class Meta:
        unique_together = ('creater', "content_type", "object_id")
    FLAG_CHOICES = (
        ('ZZ', '激进时政或意识形态话题'),
        ('SQ', '色情、淫秽或低俗内容'),
        ('AD', '广告或垃圾信息'),
        ('OT', '其他原因'),
    )
    creater = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey("content_type", "object_id")
    create_time = models.DateTimeField(auto_now_add=True)
    choice = models.CharField(max_length=2,choices=FLAG_CHOICES,default='AD')




