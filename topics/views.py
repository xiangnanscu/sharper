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

from .models import Topic, Comment
from .forms import TopicForm,CommentForm,CaptchaTopicForm,CaptchaCommentForm

from tools import paginator

PAGESIZE = getattr(settings,'PAGESIZE',10)

class TopicList(SharpListView):
    model = Topic
    response_class = TemplateResponse
    sort = 'active'
    pagesize = PAGESIZE

class TopicDetail(SharpDetailListView):
    model = Topic
    response_class = TemplateResponse
    pagesize = PAGESIZE

    def get_child_queryset(self):
        "外键model需要在子类中才能确定"
        return self.object.reply_set.all()

class TopicCreate(SharpCreateView):
    model=Topic
    form_class = lambda self:CaptchaTopicForm if getattr(self.request,'is_attack',None) else TopicForm

    def form_valid(self, form):
        self.object=form.create()
        self.object.creater=self.request.user
        self.object.save()
        form.add_tags(self.object)
        return HttpResponseRedirect(self.get_success_url())

class CommentCreate(SharpCreateView):
    model=Comment
    hoster_model=Topic
    fields=['content']
    form_class = lambda self:CaptchaCommentForm if getattr(self.request,'is_attack',None) else CommentForm

class TopicUpdate(SharpUpdateView):
    model=Topic
    form_class = TopicForm
    template_name_suffix = '_update_form'

    def get_initial(self):
        initial=super(TopicUpdate,self).get_initial()
        initial['tags']=';'.join([t.name for t in self.object.tags.all()])+';'
        return initial

    def form_valid(self, form):
        form.update(self.object)
        return HttpResponseRedirect(self.get_success_url())

class CommentUpdate(SharpUpdateView):
    model=Comment
    form_class = CommentForm
    template_name_suffix = '_update_form'
