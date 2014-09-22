import time
import json
from django.shortcuts import render_to_response
from django.template import RequestContext,Context
#from django.template.loader import get_template
from djjinja2.loader import get_template
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404,StreamingHttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError, ImproperlyConfigured
from django.db import models
from django.utils.html import escape
from django.contrib.contenttypes.models import ContentType
#from django.template.response import TemplateResponse
from djjinja2.response import TemplateResponse
from django.forms.models import model_to_dict
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic.list import ListView,MultipleObjectTemplateResponseMixin
from django.views.generic.base import ContextMixin, View

from tools import BlackMeta

class PaginationMixin(ContextMixin):
    "子类每增加一个%s_kwarg的类属性,都要定义相应的get_%s方法"
    width = 2
    pagesize = None
    sort = None
    sort_kwarg = 'sort'
    sort_dict = None
    page_kwarg = 'page'
    pagesize_kwarg = 'pagesize'

    def get_queryset(self):
        """
        Get the list of items for this view. This must be an iterable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured("'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset

    def get_processed_queryset(self):
        "应该在子类对self.get_queryset做进一步处理"
        raise NotImplemented

    def get_kwarg_list(self):
        "如果子类添加了%s_kwarg的类属性,则需要重写并调用此方法进行累加"
        return [self.page_kwarg,self.pagesize_kwarg,self.sort_kwarg]

    def get_kwarg_list_exclude(self,*excludes):
        return [v for v in self.get_kwarg_list() if v not in excludes]

    def get_kwarg_list_include(self,*includes):
        return [v for v in self.get_kwarg_list() if v in includes]

    def get_query_string(self,include=True,*args):
        "根据排除或指定的args,从self.kwargs或self.request.GET中"
        "获取形成新的url查询字符串"
        query_list=list()
        if include:
            method = self.get_kwarg_list_include 
        else:
            method = self.get_kwarg_list_exclude 
        for k in method(*args):
            attr = getattr(self,'get_%s'%k)()
            if attr is not None:
                query_list.append('%s=%s'%(k,attr))
        return '&'.join(query_list)

    def get_page(self):
        return self.kwargs.get(self.page_kwarg) \
                or self.request.GET.get(self.page_kwarg) \
                or 1

    def get_pagesize(self):
        return self.kwargs.get(self.pagesize_kwarg) \
                or self.request.GET.get(self.pagesize_kwarg) \
                or self.pagesize

    def get_sort(self):
        return self.kwargs.get(self.sort_kwarg) \
                or self.request.GET.get(self.sort_kwarg) \
                or self.sort       

    def get_page_list(self):
        total = self.total
        if not total:
            return []
        width = self.width
        page = self.page-1
        pagesize = int(self.get_pagesize())
        pages = list(range(int(total/pagesize) + (1 if total%pagesize else 0)))
        if page in pages[:width*2]:
            page_list = pages[:width*2+1] + (['...']+pages[-1:] if pages[(width+1)*2:] else [])
        elif page in pages[-width*2:]:    
            page_list = (pages[:1]+['...'] if pages[:-(width+1)*2] else []) + pages[-(width*2+1):]
        else:
            page_list = pages[:1]+['...']+pages[(page-width):(page+width+1)]+['...']+pages[-1:]
        page_list = ([] if page==pages[0] else ['prev']) +\
                    [str(p+1) if isinstance(p,int) else p for p in page_list] +\
                    ([] if page==pages[-1] else ['next'])  
        return page_list

    def get_object_list(self):
        processed_queryset = self.get_processed_queryset()
        total = self.total
        if not total:
            return processed_queryset.none()
        page = self.page-1
        pagesize = int(self.get_pagesize())
        pages = list(range(int(total/pagesize) + (1 if total%pagesize else 0)))
        if page not in pages:
            #这里有个奇特的陷阱.如果把processed_queryset.none()替换成[]
            #模板引擎会出错.已查明原因,是因为父类
            #MultipleObjectTemplateResponseMixin.get_template_names方法
            #在没有指定模板文件名的情况下,会把self.object_list视为queryset来
            #确定默认的模板文件名.
            return processed_queryset.none() 
        else:
            return processed_queryset[page*pagesize:(page+1)*pagesize]       

    def get_pagination_data(self):
        return {
                'page':getattr(self,'page',int(self.get_page())),
                'page_list':getattr(self,'page_list',self.get_page_list()),
                'object_list':getattr(self,'object_list',self.get_object_list()),
                'query_string':self.get_query_string(False,'page'),
            }

    def get_context_data(self, **kwargs):
        context = self.get_pagination_data()
        context.update(kwargs)
        return super(PaginationMixin, self).get_context_data(**context)

class SharpListView(PaginationMixin,MultipleObjectTemplateResponseMixin,View):
    "可以对包含tag外键的model进行处理"
    response_class = TemplateResponse
    queryset = None
    model = None
    tag_kwarg = 'tag'
    sort_dict={'votes':'-vote_sum','active':'-edit_time','newest':'-create_time'}

    def get(self, request, *args, **kwargs):
        self.page = int(self.get_page())
        self.total = self.get_processed_queryset().count()
        self.object_list = self.get_object_list()
        self.page_list = self.get_page_list()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_tag(self):
        return self.kwargs.get(self.tag_kwarg) \
                or self.request.GET.get(self.tag_kwarg) \
                or None  

    def get_kwarg_list(self):
        return [self.tag_kwarg]+super(SharpListView,self).get_kwarg_list()

    def get_processed_queryset(self):
        "根据url传入的参数进行tag过滤和sort排序"
        queryset = self.get_queryset()
        tag = self.get_tag()
        if tag is not None:
            queryset = queryset.filter(tags__name=tag)
        sort = self.sort_dict.get(self.get_sort(),None)
        if sort is not None:
            queryset = queryset.order_by(sort)
        #如果定义了额外的处理,则继续过滤
        if hasattr(self,'get_extra_processed_queryset'):
            queryset = self.get_extra_processed_queryset(queryset)
        return queryset

class SharpDetailListView(PaginationMixin,DetailView):
    "例如,问题的detail页面包含多个回答,而回答需要排序"
    "因此,融合detail和list视图就很有必要"

    response_class = TemplateResponse
    queryset = None
    model = None
    sort_dict={'votes':'-vote_sum','active':'-edit_time','newest':'-create_time'}

    def get(self, request, *args, **kwargs):
        "定义次序重要,不要改变"
        self.object = self.get_object()
        self.total = self.get_processed_queryset().count()
        self.page = int(self.get_page())
        self.object_list = self.get_object_list()
        self.page_list = self.get_page_list()
        
        context = self.get_context_data(object=self.object)

        return self.render_to_response(context)

    def get_processed_queryset(self):
        "这个是针对回答的排序"
        queryset = self.get_child_queryset()
        sort = self.sort_dict.get(self.get_sort(),None)
        if sort is not None:
            queryset = queryset.order_by(sort)
        #如果定义了额外的处理,则继续过滤
        if hasattr(self,'get_extra_processed_queryset'):
            queryset = self.get_extra_processed_queryset(queryset)
        return queryset

    def get_child_queryset(self):
        "外键model需要在子类中才能确定"
        raise NotImplemented

class SharpCreateView(CreateView):
    response_class = TemplateResponse
    hoster_model=None
    hoster_pk_url_kwarg='hoster_pk'
    fields=None
    ajax_form_error_template='ajax_form_errors.html'
    ajax_form_success_template='ajax_form_success.html'

    def get_form_class(self):
        if callable(self.form_class):
            return self.form_class()
        elif self.form_class:
            return self.form_class
        else:
            raise ImproperlyConfigured(
                "在定义类视图%s的时候,你必须明确指定一个form_class."%self.__class__.__name__)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        #print('kwargs',kwargs)
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.success_url:
            url = self.success_url % self.object.__dict__
        elif hasattr(self.object,'url'):
            return self.object.url
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        create_dict={'creater':self.request.user}
        if self.hoster_model is not None:
            self.hoster = self.hoster_model._default_manager.get(pk=self.kwargs[self.hoster_pk_url_kwarg])
            create_dict.update(dict(
                hoster=self.hoster,
                receiver=self.hoster.creater,)
            )
        if self.fields is None:
            fields = [field.name for field in form.visible_fields()]
        else:
            fields = self.fields
        for field in fields:
            create_dict[field]=form.cleaned_data[field]
        self.object=self.model._default_manager.create(**create_dict)
        if self.request.is_ajax():
            return self.ajax_form_valid()
        else:
            #如果存在分页,则需要知道最后一页是多少.才能
            #知道新增的回复在第几页.
            #方法get_page写在子类.
            if hasattr(self,'get_page'):
                query_string='?page=%s'%self.get_page()
                url,anchor = self.get_success_url().rsplit('#',1)
                return HttpResponseRedirect(url+query_string+'#'+anchor)
            else:
                return HttpResponseRedirect(self.get_success_url())

    def ajax_form_valid(self):
        #print('call ajax_form_valid')
        t = get_template(self.ajax_form_success_template,self.request.path)
        success_items = t.render(Context({
            'items':[self.object],
            'user':self.request.user,}))
        return HttpResponse(
                json.dumps({'form_valid':True,'success_items':success_items}), 
                content_type="application/json",
            )

    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.ajax_form_invalid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def ajax_form_invalid(self, form):
        t = get_template(self.ajax_form_error_template,self.request.path)
        error_items = t.render(Context({'form':form}))
        return HttpResponse(
                json.dumps({'form_valid':False,'error_items':error_items}), 
                content_type="application/json",
            )

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        #print('request.is_attack',request.is_attack)
        #create view在get的时候,self.object必须指定为None
        self.object = None 
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if self.request.is_ajax():
            return self.ajax_get(form)
        else:  
            return self.render_to_response(self.get_context_data(form=form))
 
    def ajax_get(self, form):
        "暂时用不到form参数.因为可以直接在客户端加载整个form"
        "更新.由于引入验证码机制,现在需要用到form参数了"
        hoster = self.hoster_model._default_manager.get(
                pk=self.kwargs[self.hoster_pk_url_kwarg])
        # 这里的get_template是重写了的,多了url参数.
        t = get_template(self.ajax_form_success_template,self.request.path)
        success_items = t.render(Context({
                'items':hoster.comment_set.all(),
                'user':self.request.user,
                'form':form,
                'url':self.request.path,
                })) 
        return HttpResponse(json.dumps({'success_items':success_items}), content_type="application/json")

class SharpUpdateView(UpdateView):
    response_class = TemplateResponse
    fields=None
    ajax_form_error_template='ajax_form_errors.html'
    ajax_form_success_template='ajax_form_success.html'

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        if self.fields is None:
            return self.object.__dict__.copy()
        else:
            return {field:getattr(self.object,field,'') for field in self.fields}

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class:
            return self.form_class
        else:
            raise ImproperlyConfigured(
                "在定义类视图%s的时候,你必须明确指定一个form_class."%self.__class__.__name__)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.success_url:
            url = self.success_url % self.object.__dict__
        elif hasattr(self.object,'url'):
            return self.object.url
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        if self.fields is None:
            self.object.__dict__.update({
                field.name:form.cleaned_data[field.name] for field in form.visible_fields()
            })
        else:
            self.object.__dict__.update({
                field:form.cleaned_data[field] for field in self.fields
            })
        self.object.save()
        if self.request.is_ajax():
            return self.ajax_form_valid()
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.ajax_form_invalid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def ajax_form_invalid(self, form):
        t = get_template(self.ajax_form_error_template,self.request.path)
        error_items = t.render(Context({'form':form}))
        return HttpResponse(
                json.dumps({'form_valid':False,'error_items':error_items}), 
                content_type="application/json",
            )

    def ajax_form_valid(self):
        t = get_template(self.ajax_form_success_template,self.request.path)
        success_items = t.render(Context({
            'items':[self.object],
            'user':self.request.user,}))
        return HttpResponse(
                json.dumps({'form_valid':True,'success_items':success_items}), 
                content_type="application/json",
            )
