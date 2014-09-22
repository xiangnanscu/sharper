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

from .models import Question, Comment,Tag
from common.forms import CommentFormBase

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 200)

class QuestionForm(forms.Form):
    """
    """
    title=forms.CharField(label="标题") 
    content=forms.CharField(label="描述")
    tag=forms.CharField(label="标签")
    
    def clean_tag(self):
        """
        """
        from re import sub
        raw_value = self.cleaned_data["tag"]
        value = sub(r'\s','',raw_value)
        if not value:
            raise ValidationError('不允许空白标签')
        value = value + ('' if value[-1] in settings.TAG_SPLITER else '|')
        if not settings.TAG_REGEX.match(value):
            raise ValidationError('标签格式不合法')
        _tags = [v for v in settings.TAG_SPLITER_REGEX.split(value) if v]
        return set(_tags)

    def get_question_object(self):
        return Question(**self.get_question_create_data())

    def get_question_create_data(self):
        return dict(
            title = self.cleaned_data["title"],
            content = self.cleaned_data["content"],
        )

    def get_or_create_tags(self):
        return [Tag.objects.get_or_create(name=name) \
                 for name in self.cleaned_data["tag"] ]

    def add_tags_for_question(self, question):
        for tag in self.add_tags_to_question():
            question.tags.add(tag)

    def update_for_question_queryset(self, qset):
        qset.update(**self.get_question_create_data())

    def update_tags_for_question(self, question):
        question.tags.all().delete()
        self.add_tags_to_question(question)

class CommentForm(CommentFormBase):
    """
    """
    pass
