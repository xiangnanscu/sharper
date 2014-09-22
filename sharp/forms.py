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



class BaseForm(forms.Form):
    """
    """
    self_address = forms.CharField(widget=forms.HiddenInput)
    hoster_address = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, self_address, hoster_address='', data=None, initial=None, label_suffix=''):
        self.self_address = self_address
        self.hoster_address = hoster_address
        if initial is None:
            initial = {'self_address':self_address,'hoster_address':hoster_address}        
        super(BaseForm, self).__init__(data=data, initial=initial, label_suffix=label_suffix)

    def clean_content(self):
        """
        言论审核
        """
        content = self.cleaned_data["content"]
        if settings.COMMENTS_ALLOW_PROFANITIES == False:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in content.lower()]
            if bad_words:
                raise forms.ValidationError('内容包含敏感词汇,无法提交')
        return content