from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.template import RequestContext,Context
from django.conf import settings
User = get_user_model()

#from django.db import models
#from django.db.models import Count,Sum
#from django.contrib.contenttypes.models import ContentType
from common.classviews import SharpCreateView,SharpUpdateView
from questions.models import Question
from .models import Answer, Comment
from .forms import AnswerForm, CommentForm,CaptchaCommentForm,CaptchaAnswerForm
from tools import paginator

PAGESIZE = getattr(settings,'PAGESIZE',10)

class AnswerCreate(SharpCreateView):
    model=Answer
    hoster_model=Question
    fields=['content']
    form_class = lambda self:CaptchaAnswerForm if getattr(self.request,'is_attack',None) else AnswerForm
    ajax_form_success_template='ajax_re_success.html'

    def get_page(self):
        total = self.hoster.answer_set.count()
        return int(total/PAGESIZE) + (1 if total%PAGESIZE else 0)

class CommentCreate(SharpCreateView):
    model=Comment
    hoster_model=Answer
    fields=['content']
    form_class = lambda self:CaptchaCommentForm if getattr(self.request,'is_attack',None) else CommentForm

class AnswerUpdate(SharpUpdateView):
    model=Answer
    form_class = AnswerForm
    template_name_suffix = '_update_form'
    ajax_form_success_template='ajax_re_success.html'

class CommentUpdate(SharpUpdateView):
    model=Comment
    form_class = CommentForm
    template_name_suffix = '_update_form'