import time
from django import forms
from django.forms.util import ErrorDict
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.encoding import force_text
from django.utils.text import get_text_list
from django.utils import timezone
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _
from django.core.exceptions import ValidationError

from captcha.fields import CaptchaField
from .models import Question, Comment,Tag


COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 200)
COMMENT_MIN_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3)
TAG_MAX_LENGTH = getattr(settings,'TAG_MAX_LENGTH', 7)
QUESTION_CONTENT_MAX_LENGTH = getattr(settings,'QUESTION_CONTENT_MAX_LENGTH', 2000)
QUESTION_CONTENT_MIN_LENGTH = getattr(settings,'QUESTION_CONTENT_MIN_LENGTH', 3)
QUESTION_TITLE_MAX_LENGTH = getattr(settings,'QUESTION_TITLE_MAX_LENGTH', 30)
QUESTION_TITLE_MIN_LENGTH = getattr(settings,'QUESTION_TITLE_MIN_LENGTH', 3)

from common.forms import BaseCommentForm

class CommentForm(BaseCommentForm):
    """
    """

class CaptchaCommentForm(CommentForm):
    captcha = CaptchaField(label='')

class QuestionForm(forms.Form):
    """
    """
    title=forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'placeholder':'点击这里输入问题标题',
            'rows':1,
            'cols': 80,
        }),
        max_length=QUESTION_TITLE_MAX_LENGTH,
    ) 
    content=forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'placeholder':'点击这里输入问题内容',
            'rows':20,
            'cols': 80,
        }),
        max_length=QUESTION_CONTENT_MAX_LENGTH,
    ) 
    tags=forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'placeholder':'为该问题选择1到%s个标签,多个标签用逗号或分号分隔'%TAG_MAX_LENGTH,
            'rows':1,
            'cols': 80,
        }),
    ) 

    def clean_title(self):
        """
        言论审核
        """
        title = self.cleaned_data["title"]
        if not QUESTION_TITLE_MIN_LENGTH<=len(title)<=QUESTION_TITLE_MAX_LENGTH:
            raise forms.ValidationError('字符数不合法')
        if settings.COMMENTS_ALLOW_PROFANITIES == False:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in title.lower()]
            if bad_words:
                raise forms.ValidationError('内容不合法')
        return title

    def clean_content(self):
        """
        言论审核
        """
        content = self.cleaned_data["content"]
        if not QUESTION_CONTENT_MIN_LENGTH<=len(content)<=QUESTION_CONTENT_MAX_LENGTH:
            raise forms.ValidationError('字符数不合法')
        if settings.COMMENTS_ALLOW_PROFANITIES == False:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in content.lower()]
            if bad_words:
                raise forms.ValidationError('内容不合法')
        return content

    def clean_tags(self):
        """
        检测tag字符串是否符合规则,并将其转化为集合.
        例如:"创业;投资" -> {"创业","投资"}
        """
        from re import sub
        raw_value = self.cleaned_data["tags"]
        value = sub(r'\s','',raw_value)
        if not value:
            raise ValidationError('不允许空白标签')
        value = value + ('' if value[-1] in settings.TAG_SPLITER else '|')
        if not settings.TAG_REGEX.match(value):
            raise ValidationError('标签格式不合法') #这里就已经包含了标签数的检测
        return {v for v in settings.TAG_SPLITER_REGEX.split(value) if v}


    def create(self):
        return Question(**self.get_create_data())

    def get_create_data(self):
        return dict(
            title = self.cleaned_data["title"],
            content = self.cleaned_data["content"],
        )

    def update(self,obj):
        #更新标题和正文
        for k,v in self.get_create_data().items():
            setattr(obj,k,v)
        obj.save()
        #更新标签
        self.update_tags(obj)

    def update_tags(self,obj):
        if self.cleaned_data["tags"] == {t.name for t in obj.tags.all()}:
            #print("没有修改标签,无需进行")
            return
        obj.tags.clear()
        self.add_tags(obj)

    def add_tags(self,obj):
        for tag in self.get_or_create_tags():
            obj.tags.add(tag)

    def get_or_create_tags(self):
        return [Tag.objects.get_or_create(name=name)[0] \
                 for name in self.cleaned_data["tags"] ]

class CaptchaQuestionForm(QuestionForm):
    captcha = CaptchaField(label='')