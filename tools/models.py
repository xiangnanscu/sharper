from django.contrib.auth import get_user_model
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

import tools


class ActionAbstractModel(models.Model):
    """
    通用行为类的基类,比如投票,评论,标记,举报

    三个属性:
    1.行为发起者--user
    2.行为作用对象--content_object
    3.行为发生时间--create_time

    一个方法:
    1.显示该行为的url.
    """
    class Meta:
        abstract = True

    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
    	verbose_name=_('user'), 
    	)
    # Content-object field
    content_type = models.ForeignKey(ContentType,
            verbose_name=_('content type'),
            related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey("content_type", "object_id")
    create_time = models.DateTimeField(auto_now_add=True)


    def get_redirect(self,viewname=None,args=None):
        if viewname is None:
            viewname = '%s-url'%self._meta.model_name  
        if args is None:
            args = (self.content_type, self.object_id)  
        return urlresolvers.reverse(viewname,args=args,)

class BasePostAbstractModel(models.Model):
    """
    文本类的基类,至少有一个内容字段.比如问题,答案,帖子,博客
    """
    class Meta:
        abstract=True

    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
        verbose_name=_('user'), 
        )
    create_time = models.DateTimeField(auto_now_add=True)  
    last_edit_time = models.DateTimeField(auto_now=True)  
    content = models.TextField(
        verbose_name=_('内容'),
        max_length=5000,
        validators=[
        tools.LengthRangeValidator(1,5000),
        validators.RegexValidator(
            regex=tools.word_regex, 
            message=_('内容包含非法字符'),
            ),
        ],
        )  
