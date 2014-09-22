from django.shortcuts import render
from django.shortcuts import render_to_response
#from django.template.response import TemplateResponse
from djjinja2.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
#from django.db import models
#from django.db.models import Count,Sum
#from django.contrib.contenttypes.models import ContentType
from common.classviews import SharpCreateView,SharpUpdateView,SharpListView,SharpDetailListView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Question, Comment
from .forms import QuestionForm,CommentForm,CaptchaQuestionForm,CaptchaCommentForm

import time
from tools import paginator,meta,Print

def test(request,num):
    print('call test')
    return HttpResponse("%s,cached %s"%(num,time.ctime()))

PAGESIZE = getattr(settings,'PAGESIZE',10)

class QuestionList(SharpListView):
    model = Question
    response_class = TemplateResponse
    sort = 'newest'
    pagesize = PAGESIZE
#QuestionList.printize()

class QuestionDetail(SharpDetailListView):
    model = Question
    response_class = TemplateResponse
    pagesize = PAGESIZE

    def get_child_queryset(self):
        "外键model需要在子类中才能确定"
        return self.object.answer_set.all()

#QuestionDetail.printize()

class QuestionCreate(SharpCreateView):
    model=Question
    form_class = lambda self:CaptchaQuestionForm if getattr(self.request,'is_attack',None) else QuestionForm

    def form_valid(self, form):
        self.object=form.create()
        self.object.creater=self.request.user
        self.object.save()
        form.add_tags(self.object)
        return HttpResponseRedirect(self.get_success_url())

class CommentCreate(SharpCreateView): 
    model=Comment
    hoster_model=Question
    fields=['content']
    form_class = lambda self:CaptchaCommentForm if getattr(self.request,'is_attack',None) else CommentForm

class QuestionUpdate(SharpUpdateView):
    model=Question
    form_class = QuestionForm
    template_name_suffix = '_update_form'

    def get_initial(self):
        initial=super(QuestionUpdate,self).get_initial()
        initial['tags']=';'.join([t.name for t in self.object.tags.all()])+';'
        #print('initial',initial)
        return initial

    def form_valid(self, form):
        form.update(self.object)
        return HttpResponseRedirect(self.get_success_url())

class CommentUpdate(SharpUpdateView):
    model=Comment
    form_class = CommentForm
    template_name_suffix = '_update_form'
