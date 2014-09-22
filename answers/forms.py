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
from .models import Answer, Comment

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 200)
COMMENT_MIN_LENGTH = getattr(settings,'COMMENT_MIN_LENGTH', 3)
TAG_MAX_LENGTH = getattr(settings,'TAG_MAX_LENGTH', 7)
ANSWER_CONTENT_MAX_LENGTH = getattr(settings,'ANSWER_CONTENT_MAX_LENGTH', 2000)
ANSWER_CONTENT_MIN_LENGTH = getattr(settings,'ANSWER_CONTENT_MIN_LENGTH', 3)
ANSWER_TITLE_MAX_LENGTH = getattr(settings,'ANSWER_TITLE_MAX_LENGTH', 30)
ANSWER_TITLE_MIN_LENGTH = getattr(settings,'ANSWER_TITLE_MIN_LENGTH', 3)

from common.forms import BaseCommentForm
class CommentForm(BaseCommentForm):
    """
    """

class CaptchaCommentForm(CommentForm):
    captcha = CaptchaField(label='')

class AnswerForm(forms.Form):
    """
    """
    content=forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'placeholder':'点击这里输入答案内容',
            'rows':6,
            'cols': 75,
        }),
        max_length=ANSWER_CONTENT_MAX_LENGTH,
    ) 
    def clean_content(self):
        """
        言论审核
        """
        content = self.cleaned_data["content"]
        if not ANSWER_CONTENT_MIN_LENGTH<=len(content)<=ANSWER_CONTENT_MAX_LENGTH:
            raise forms.ValidationError('字符数不合法')
        if settings.COMMENTS_ALLOW_PROFANITIES == False:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in content.lower()]
            if bad_words:
                raise forms.ValidationError('内容不合法')
        return content   

class CaptchaAnswerForm(AnswerForm):
    captcha = CaptchaField(label='')
