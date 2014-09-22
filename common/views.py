import time
import json
from django.shortcuts import render_to_response
from django.template import RequestContext,Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404,StreamingHttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.html import escape
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.template.response import TemplateResponse

def get_hoster(app_label,model_name,object_id):
    print('call get_hoster')
    try:
        model = models.get_model(app_label,model_name)
        hoster = model._default_manager.get(pk=object_id)
        return hoster
    except Exception as e: 
        print('fail, becuase:',e)
        return None

def vote(request):
    print('call vote')
    data = request.POST.copy()
    print('data',data)
    creater = request.user
    if creater.reputation < 1:
        print('必须大于等于11的声望才能进行投票操作')
        return None
    hoster=data.get("hoster")
    print('data.get("value")',type(data.get("value")),data.get("value"))
    value=int(data.get("value"))
    print('hoster',hoster)
    app_label,model_name,object_id=hoster.split('-')
    print('app_label,model_name,object_id',app_label,model_name,object_id)
    hoster = get_hoster(app_label,model_name,object_id)
    print('ok')
    receiver = hoster.creater
    if creater == receiver:
        print('不能对自己创建的条目投票')
        return #不能对自己创建的条目投票
    if hoster.vote_set.filter(creater=creater).exists():
        print('一人只允许投一次,且不可更改')
        return #一人只允许投一次,且不可更改
    print('user is legal')
    vote_model = ContentType.objects.get(app_label=app_label, model="vote").model_class()
    vote = vote_model.objects.create(
        creater=creater,
        receiver=receiver,
        hoster=hoster,
        value=value,
    )
    print('hoster.vote_sum',hoster.vote_sum)
    print('value',value)
    # hoster_set.update(vote_sum=hoster.vote_sum+value) 
    hoster.vote_sum += value
    hoster.save(update_fields=['vote_sum'])
    print('hoster.vote_sum',hoster.vote_sum)
    print('receiver.reputation',receiver.reputation)
    reputation_change = 5 if value==1 else -2
    print('reputation_change',reputation_change)
    receiver.reputation += reputation_change
    receiver.save(update_fields=['reputation'])
    print('receiver.reputation',receiver.reputation)
    if value==-1:#踩别人自身需要消耗声望
        print('creater.reputation',creater.reputation)
        creater.reputation -= 1
        creater.save(update_fields=['reputation'])
        print('creater.reputation',creater.reputation)
    res='%s@%s'%(hoster.vote_sum,receiver.reputation)
    print('res',res)
    return HttpResponse(res)  

def vote(request):
    data = request.POST.copy()
    creater = request.user
    if creater.reputation < 1:
        return None
    hoster=data.get("hoster")
    value=int(data.get("value"))
    app_label,model_name,object_id=hoster.split('-')
    hoster = get_hoster(app_label,model_name,object_id)
    receiver = hoster.creater
    if creater == receiver:
        return #不能对自己创建的条目投票
    if hoster.vote_set.filter(creater=creater).exists():
        return #一人只允许投一次,且不可更改
    vote_model = ContentType.objects.get(app_label=app_label, model="vote").model_class()
    vote = vote_model.objects.create(
            creater=creater,
            receiver=receiver,
            hoster=hoster,
            value=value,
        )
    # hoster_set.update(vote_sum=hoster.vote_sum+value) 
    hoster.vote_sum += value
    hoster.save(update_fields=['vote_sum'])
    reputation_change = 5 if value==1 else -2
    receiver.reputation += reputation_change
    receiver.save(update_fields=['reputation'])
    if value==-1:#踩别人自身需要消耗声望
        creater.reputation -= 1
        creater.save(update_fields=['reputation'])
    res='%s@%s'%(hoster.vote_sum,receiver.reputation)
    return HttpResponse(res) 

def favor(request):
    print('call favor')
    data = request.POST.copy()
    creater = request.user
    hoster=data.get("hoster")
    app_label,model_name,object_id=hoster.split('-')
    hoster = get_hoster(app_label,model_name,object_id)
    favor_model = ContentType.objects.get(app_label=app_label, model="favor").model_class()
    favor,_ = favor_model.objects.get_or_create(
            creater=creater,
            hoster=hoster,)
    if favor.is_favor:
        favor.is_favor = False  
        hoster.favor_count += -1
    else:
        favor.is_favor = True  
        hoster.favor_count += 1
    favor.save()
    hoster.save(update_fields=['favor_count'])
    return HttpResponse(hoster.favor_count) 

def accept(request):
    print('call accept')
    data = request.POST.copy()
    #print(data)
    creater = request.user
    hoster=data.get("hoster")
    app_label,model_name,object_id=hoster.split('-')
    hoster = get_hoster(app_label,model_name,object_id)
    question = hoster.hoster
    receiver = hoster.creater
    #print('question.accept_pk',question.accept_pk)
    question.accept_pk = hoster.pk
    question.save(update_fields=['accept_pk'])
    #print('question.accept_pk',question.accept_pk)
    reputation_change = 10 
    receiver.reputation += reputation_change
    receiver.save(update_fields=['reputation'])
    return HttpResponse(str(receiver.reputation))
 