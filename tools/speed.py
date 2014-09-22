import random
import time
import os
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
from django.db.models import Count, Sum

from questions.models import Vote as qv, Favor as qf, Comment as qc, Question, Tag
from answers.models import Vote as av, Favor as af, Comment as ac, Answer
 
cp = os.path.dirname(__file__)

def ranrange(arr): 
    size=list(range(len(arr)))
    return random.sample(arr, random.choice(size))

def ranone(arr):
    return random.choice(arr)

def init():
    now = timezone.now()
    u=User.objects.create(username='xn',email='280145668@qq.com',password='111qqq',is_active=True,)
    u.set_password('111qqq')
    u.save()
    for i in range(5):
        u=User.objects.create(username='测试用户%s'%i,email='test%s@163.com'%i,password='111qqq',is_active=True,)        
        u.set_password('111qqq')
        u.save()
    with open(os.path.join(cp,'comments.txt'),encoding='u8') as f:
        clist=[line for line in f.read()[1:].split('\n')][:-3]    
    with open(os.path.join(cp,'answers.txt'),encoding='u8') as f:
        alist=[line for line in f.read().split('\n')][:-1]
    with open(os.path.join(cp,'questions.txt'),encoding='u8') as f:
        qlist=[line.split('\t') for line in f.read().split('\n')][:-20]

    ulist=[u for u in User.objects.all()]

    total=len(qlist)
    step=0
    for t,c in qlist:
        step+=1
        print(' %s %% done....'%int(step*100.0/total))
        q=Question.objects.create(creater=ranone(ulist),title=t,content=c,)
        for cc in ranrange(clist)[:5]:
            qc.objects.create(creater=ranone(ulist),hoster=q,content=cc,receiver=q.creater)
        for u in ranrange(ulist):
            Answer.objects.create(creater=u,hoster=q,content=ranone(alist),receiver=q.creater)
        for tag in [Tag.objects.get_or_create(name=name)[0] for name in list(ranrange(['烦恼','爱情','困惑','婚姻','创业','迷惑','悲伤']))[1:5]]:
            q.tags.add(tag)
        # for u in ranrange(ulist):
        #     qv.objects.create(creater=u,hoster=q,value=ranone([-1,1]),receiver=q.creater)                        
        for u in ranrange(ulist):
            qf.objects.create(creater=u,hoster=q,is_favor=True) 
        answers=q.answer_set.all()
        for a in answers:
            for cc in ranrange(clist)[:5]:
                ac.objects.create(creater=ranone(ulist),hoster=a,content=cc,receiver=a.creater)
            # for u in ranrange(ulist):
            #     av.objects.create(creater=u,hoster=a,value=ranone([-1,1]),receiver=a.creater) 
            for u in ranrange(ulist):
                af.objects.create(creater=u,hoster=a,is_favor=True)
    # for q in Question.objects.all():
    #     q.vote_sum=sum([v.value for v in q.vote_set.all()])
    #     q.favor_count=sum([1 for f in q.favor_set.all() if f.is_favor])
    #     q.save()
    # for a in Answer.objects.all():
    #     a.vote_sum=sum([v.value for v in a.vote_set.all()])
    #     a.favor_count=sum([1 for f in a.favor_set.all() if f.is_favor])
    #     a.save()
def update():
    for q in Question.objects.all():
        q.vote_sum=sum([v.value for v in q.vote_set.all()])
        q.favor_count=sum([1 for f in q.favor_set.all() if f.is_favor])
        q.save()
    for a in Answer.objects.all():
        a.vote_sum=sum([v.value for v in a.vote_set.all()])
        a.favor_count=sum([1 for f in a.favor_set.all() if f.is_favor])
        a.save()
    for u in User.objects.all():
        u.set_password('111qqq')
        u.save()        
def test():
    us=User.objects.all()
    qs=Question.objects.all()
    ans=Answer.objects.all()
    vs=Vote.objects.all()
    cs=Comment.objects.all()
    u1,u2,u3=us[:3]
    q1,q2,q3=qs[:3]
    a1,a2,a3=ans[:3]
    c1,c2,c3=cs[:3]
    return locals().copy()

def uget(pk):
    return User.objects.get(pk=pk)

def qget(pk):
    return Question.objects.get(pk=pk)

def aget(pk):
    return Answer.objects.get(pk=pk)
