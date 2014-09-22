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
from topics.models import Topic
from .models import Reply, Comment
from .forms import ReplyForm, CommentForm,CaptchaCommentForm, CaptchaReplyForm
from tools import paginator

PAGESIZE = getattr(settings,'PAGESIZE',10)

class ReplyCreate(SharpCreateView):
    model=Reply
    hoster_model=Topic
    fields=['content']
    form_class = lambda self:CaptchaReplyForm if getattr(self.request,'is_attack',None) else ReplyForm
    ajax_form_success_template='ajax_re_success.html'

    def get_page(self):
        total = self.hoster.reply_set.count()
        return int(total/PAGESIZE) + (1 if total%PAGESIZE else 0)

class CommentCreate(SharpCreateView):
    model=Comment
    hoster_model=Reply
    fields=['content']
    form_class = lambda self:CaptchaCommentForm if getattr(self.request,'is_attack',None) else CommentForm

class ReplyUpdate(SharpUpdateView):
    model=Reply
    form_class = ReplyForm
    template_name_suffix = '_update_form'
    ajax_form_success_template='ajax_re_success.html'

class CommentUpdate(SharpUpdateView):
    model=Comment
    form_class = CommentForm
    template_name_suffix = '_update_form'