import re
from datetime import datetime,date
from django.core import urlresolvers
from django.conf import settings
from django.utils.html import avoid_wrapping
from django.utils.timezone import is_aware, utc


#----以上区域专门用于加载模块变量,不要在其他区域加载-----
#----以下区域定义按需加载的常量和函数-----



#----以上区域定义按需加载的常量和函数-----
exclude=list(locals())
#----以下区域定义全局常量和函数-----

STATIC_URL=settings.STATIC_URL

def this_is_jinja2():
    return ''

def url(viewname,args=None,kwargs=None,**extra_kwargs):
    if args is None:
        args=tuple()
    if kwargs is None:
        kwargs=dict()
    kwargs.update(extra_kwargs)
    return urlresolvers.reverse(viewname,args=args,kwargs=kwargs)

#用于注册Python内建函数的字典
built_in={

    #'isinstance':isinstance,
}

#----以上区域定义全局常量和函数-----
dicts={} if not built_in else built_in.copy()
exclude.extend(['dicts','exclude','built_in'])
dicts.update({k:v for k,v in locals().items() if k not in exclude})
#print('dicts',type(dicts),dicts)
exclude.extend(list(locals()))

#----以下区域定义全局filter-----

def cut(s,num=15,tail='...'):
    if s[num:]:
        return s[:num-3]+tail
    return s

def csrf(value):
    return '<input type="hidden" name="csrfmiddlewaretoken" value="%s">'%value
    
def empty(value,string='0'):
    "默认把None之类的变量转换为0"
    return string if not value else value

def only_words(value):
    "删除所有非字符,比如空格,标点"
    return re.sub(r'\W','',str(value))

def strftime(time,strf="%Y-%m-%d %H:%M:%S"):
    "把datetime转换为易读的格式"
    return time.strftime(strf)

def timesince(d, now=None, reversed=False):
    """
    时刻d距今的秒数,翻译为人类易读的格式.
    例如3600秒翻译为"小时",2592000秒翻译为"月"
    """
    chunks = (
        (60 * 60 * 24 * 365, '%d年'),
        (60 * 60 * 24 * 30, '%d月'),
        (60 * 60 * 24 * 7, '%d周'),
        (60 * 60 * 24, '%d天'),
        (60 * 60, '%d小时'),
        (60, '%d分钟'),
    )
    # Convert date to datetime for comparison.
    if not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime):
        now = datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.now(utc if is_aware(d) else None)

    delta = (d - now) if reversed else (now - d)
    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return avoid_wrapping('0分钟')
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    result = avoid_wrapping(name % count)
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result += avoid_wrapping(name2 % count2)
    return result

def timeuntil(d, now=None):
    return timesince(d, now, reversed=True)

def naturaltime(value):
    """
    django内建函数的汉化版
    """
    if not isinstance(value, date): # datetime is a subclass of date
        return value

    now = datetime.now(utc if is_aware(value) else None)
    if value < now:
        delta = now - value
        if delta.days != 0:
            return '%(delta)s前'% {'delta': timesince(value, now)}
        elif delta.seconds == 0:
            return '现在'
        elif delta.seconds < 60:
            return '%(count)s秒前' % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return '%(count)s分钟前' % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return '%(count)s小时前'% {'count': count}
    else:
        delta = value - now
        if delta.days != 0:
            return '%(delta)s后' % {'delta': timeuntil(value, now)}
        elif delta.seconds == 0:
            return '现在'
        elif delta.seconds < 60:
            return '%(count)s秒后' % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return '%(count)s分钟后' % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return '%(count)s小时后'% {'count': count}


#----以上区域定义全局filter-----

filters={}
exclude.append('filters')
filters.update({k:v for k,v in locals().items() if k not in exclude})
#print('filters',type(filters),filters)