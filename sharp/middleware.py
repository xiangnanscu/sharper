import datetime
from django.conf import settings

datetime_now = datetime.datetime.now

USER_POST_INFO={}
CHECK_SECONDS=getattr(settings,'CHECK_SECONDS',60)
ALLOW_TIMES=getattr(settings,'ALLOW_TIMES',3)

class AntiAttackMiddleware(object):

    def process_response(self, request, response):
        user = getattr(request,"user",None)
        if user is None:
            print("None")
            return response
        if request.method == "POST" and user.is_authenticated():
            now = datetime_now()
            if user.pk not in USER_POST_INFO:
                USER_POST_INFO[user.pk]={
                    'time':now,
                    'total':0,
                    'attack':False,
                }
            d = USER_POST_INFO[user.pk]
            if d['time'] + datetime.timedelta(seconds=CHECK_SECONDS) > now :
                d['total'] +=1
                if d['total']>=ALLOW_TIMES and d['attack']==False:
                    d['attack']=True
            else:
                d['total']=1
                d['attack']=True if ALLOW_TIMES==1 else False
        #print('in response,',USER_POST_INFO)
            d['time']=now
        return response

    def process_request(self, request):

        user = getattr(request,"user",None)
        if user is None:
            return 
        if user.is_authenticated():
            if user.pk not in USER_POST_INFO:
                request.is_attack=False
            else:
                d = USER_POST_INFO[user.pk]
                if d['time'] + datetime.timedelta(seconds=CHECK_SECONDS) > datetime_now():
                    request.is_attack=d['attack']
                else:
                    request.is_attack=False

class PrintSessionMiddleware(object):
    def process_request(self, request):
        ""
        #[print('%s->%s'%(k,v))for k,v in request.session.items()]
        #[print('%s->%s'%(k,request.META[k]))for k in sorted(request.META)]
        # print(request.META['QUERY_STRING'])
        # print(request.GET)
        # print('-'*30)
        pass


