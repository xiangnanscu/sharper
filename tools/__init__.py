#!/usr/bin/env python
import os
import sys,re
from django.utils.timezone import now as datetime_now
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

import functools

def print_and_showbug(func):
    @functools.wraps(func)
    def magic(self,*args,**kwargs):
        try:
            print('call -> %s'%func.__name__)
            return func(self,*args,**kwargs)
        except Exception as e:
            print('  '+str(e))
            raise 
    return magic

import types

func_types = (types.FunctionType,types.BuiltinFunctionType,
    types.BuiltinMethodType,types.LambdaType,types.MethodType)

class BlackMeta(type):
    def __new__(cls, name, parents, attrs):
        new_attrs={}
        for par in parents:
            #print(par.__name__)
            for k,v in par.__dict__.items():
                if type(v) in func_types:
                    #print(k,v)
                    new_attrs[k] = print_and_showbug(v)
                else:
                    new_attrs[k] = v            
        for k,v in attrs.items():
            #print(k,v)
            if type(v) in func_types:
                #print(k,v)
                new_attrs[k] = print_and_showbug(v)
            else:
                new_attrs[k] = v
        return type.__new__(cls, name, parents, new_attrs)

class meta(metaclass=BlackMeta):
    pass

import inspect
class Print(object):
    @classmethod
    def printize(cls,):
        for name,attr in inspect.getmembers(cls):
            if not name.startswith('__') and type(attr) in func_types:
                setattr(cls,name,print_and_showbug(attr))

def showbug(func):
    def magic(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print(e)
            raise RuntimeError
    return magic
    
def printdir(obj):
    atd= []
    for d in dir(obj):
        try:
            print('%s->%s'%(d,getattr(obj,d)()))
        except Exception as e:
            print('%s->%s'%(d,getattr(obj,d)))
            
def AttrInspect(obj,filepath):
    atd= []
    for d in dir(obj):
        try:
            atd.append([d,getattr(obj,d)])
        except Exception as e:
            print(d,e)
            pass
    types=list(set([ type(i[1]) for i in atd]))
    with open(filepath,'w',encoding='u8') as f:
        for t in types:
            for name,obj in atd:
                if type(obj)==t:
                    f.write('%s,%s,%s\n'%(name,t,obj,))
                        
def paginator(queryset, page=1, pagesize=3,width=2):
    '''输出2个用于控制页码器的列表.
    page表示应该当前页码,queryset表示对象集合.
    page_list表示当前页的页脚应该是怎样的一个排列.
    item_list表示当前页应该显示的对象集合.
    page_list=['prev', '1', '...', '3', '4', '5', '6', '7', '...', '11', 'next']
    item_list=[queryset[12], queryset[13], queryset[14]]
    page_list首元素从'1'开始计算,item_list首元素从0开始计算.
    '''
    total=len(queryset)
    page=int(page)-1
    pages = list(range(int(total/pagesize) + (1 if total%pagesize else 0)))
    if not total or (page not in pages):
        return [],[]
    if page in pages[:width*2]:
        page_list = pages[:width*2+1] + (['...']+pages[-1:] if pages[(width+1)*2:] else [])
    elif page in pages[-width*2:]:    
        page_list = (pages[:1]+['...'] if pages[:-(width+1)*2] else []) + pages[-(width*2+1):]
    else:
        page_list = pages[:1]+['...']+pages[(page-width):(page+width+1)]+['...']+pages[-1:]
    page_list = ([] if page==pages[0] else ['prev']) +\
                [str(p+1) if isinstance(p,int) else p for p in page_list] +\
                ([] if page==pages[-1] else ['next'])  
    item_list=queryset[page*pagesize:(page+1)*pagesize]       
    return page_list,item_list

    
if __name__ == "__main__":
    pagesize=3
    for total in range(1,34,3):        
        pages=list(range(int(total/pagesize) + (1 if total%pagesize else 0)))
        for page in pages:
            page_list,item_list=paginator(page=page+1,total=total,pagesize=pagesize,width=2)
            print(page_list,item_list)
