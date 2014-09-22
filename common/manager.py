from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

class CommonQuerySet(QuerySet):

    NUMBER_TYPE_SET=set([
        'DecimalField','FloatField','BigIntegerField', 
        'CommaSeparatedIntegerField', 'IntegerField', 'PositiveIntegerField', 
        'PositiveSmallIntegerField', 'SmallIntegerField'])

    class ArgumentException(Exception):
        def __init__(self,k=0,errors=None,fields=None):
            self.errors = map(str,errors)
            self.fields = fields
            self.k = k

        def get_duplicate(self,arr):
            for e in set(arr):
                arr.remove(e)
            return ','.join(set(arr))

        def __str__(self):
            if self.k==0:
                return '你不能同时为*args和**kwargs设定参数.'
            if self.k==1:
                return '关联表名%s存在重复值.'%self.get_duplicate(self.errors)
            if self.k==2:
                return '注释名%s存在重复值.'%self.get_duplicate(self.errors)
            if self.k==3:              
                return '非法参数:%s,合法参数是:%s.\n注意,请直接传入model_name,不要使用related_query_name.'%(
                    ','.join(self.errors),
                    ','.join(self.fields),
                )

    def __init__(self,*args,**kwargs):
        super(CommonQuerySet,self).__init__(*args,**kwargs)
        self.query_meta = """
                    IFNULL((
                    SELECT %%s(%%s)  
                    FROM %%s f
                    WHERE f.%s_id = %s.id),0)
                    """%(self.model._meta.model_name,self.model._meta.db_table,)
                    # question, flash_question
        self.foreignkey_dict={r.var_name:r for r in self.model._meta.get_all_related_objects()}
        # ['answer', 'tag', 'comment', 'vote', 'favor', 'flag']
        
    def annotate_foreignkeys(self,aggregate_function='SUM',*args,**kwargs):
        """
        超级智能外键注释器(健壮版).有了它,生活更美好.
        """
        if args and kwargs:
            raise self.ArgumentException(0)
        A = set(self.foreignkey_dict)
        select_dict = {}
        if args:
            B = set(args)
            C = B-A
            if C:
                raise self.ArgumentException(3,C,A)
            if len(B)!=len(args):
                raise self.ArgumentException(1,list(args))
            for related_name in args:
                annotate_name = '%s_%s'%(related_name,aggregate_function.lower())
                r = self.foreignkey_dict[related_name]
                for f in r.opts.fields:
                    if f.get_internal_type() in self.NUMBER_TYPE_SET:
                        query = self.query_meta % (
                                aggregate_function,
                                f.name,
                                r.opts.db_table,
                            )
                        #print('r.opts == r.opts.model._meta',r.opts == r.opts.model._meta)
                        select_dict[annotate_name]=query  
                        break
                else:
                    query = self.query_meta % ('COUNT','*',r.opts.db_table,)
                    annotate_name = '%s_count'%(related_name)
                    select_dict[annotate_name]=query 
        elif kwargs: 
            B = set(kwargs)
            C = B-A
            if C:
                raise self.ArgumentException(3,C,A)          
            values = list(kwargs.values())
            if len(B)!=len(set(values)):
                raise self.ArgumentException(2,values)
            for related_name,annotate_name in kwargs.items():
                r = self.foreignkey_dict[related_name]
                for f in r.opts.fields:
                    if f.get_internal_type() in self.NUMBER_TYPE_SET:
                        query = self.query_meta % (
                                aggregate_function,
                                f.name,
                                r.opts.db_table,
                            )
                        select_dict[annotate_name]=query  
                        break
                else:
                    query = self.query_meta % ('COUNT','*',r.opts.db_table,)
                    select_dict[annotate_name]=query 
        else:
            for model_name, r in self.foreignkey_dict.items():
                annotate_name = '%s_%s'%(model_name,aggregate_function.lower())
                for f in r.opts.fields:
                    if f.get_internal_type() in self.NUMBER_TYPE_SET:
                        query = self.query_meta % (
                                aggregate_function,
                                f.name,
                                r.opts.db_table,
                            )
                        select_dict[annotate_name]=query  
                        break
                else:
                    query = self.query_meta % ('COUNT','*',r.opts.db_table,)
                    annotate_name = '%s_count'%(model_name)
                    select_dict[annotate_name]=query  
        #[print(k,v) for k,v in select_dict.items()]               
        return self.extra(select=select_dict)

    def annotate_foreignkeys_by_tuple(self,*annotate_args):
        #print('in QuerySet, call self.model._meta.db_table',self.model._meta.db_table)
        query_meta="""
                    IFNULL((
                    SELECT %%s(%%s)  
                    FROM %%s f
                    WHERE f.%s_id = %s.id),0)
                   """%(self.model._meta.model_name,self.model._meta.db_table,)
        select_dict={}
        for aggregate_function,model_class,aggregate_field in annotate_args: #SUM,Vote,value
            if isinstance(model_class,str):
                app_name,model_name = model_class.split(':')
                model_class = models.get_model(app_name,model_name)
            related_table_name = model_class._meta.db_table #flash_vote
            related_model_name = model_class._meta.model_name #vote
            annotate_name = '%s_%s'%(related_model_name,aggregate_function.lower())
            query = query_meta % (
                    aggregate_function,
                    aggregate_field,
                    related_table_name,
                )
            select_dict[annotate_name]=query
            #print(annotate_name,query)
        return self.extra(select=select_dict)

class CommonManager(models.Manager):

    def get_queryset(self):
        return CommonQuerySet(self.model, using=self._db)

    def annotate_foreignkeys_by_tuple(self,*annotate_args):
        return self.get_queryset().annotate_foreignkeys_by_tuple(*annotate_args)

    def annotate_foreignkeys(self,aggregate_function='SUM',*args,**kwargs):
        return self.get_queryset().annotate_foreignkeys(aggregate_function,*args,**kwargs)

class CommentManager(models.Manager):

    @property
    def foreign_model_dict(self):
        if not hasattr(self,'_foreign_dict'):
            res = {}
            for f in self.model._meta.fields:
                if hasattr(f,'get_path_info'):
                    print('work')
                    h = f.get_path_info()[0].to_opts
                    res['%s-%s'%(h.app_label,h.model_name)]=f.name
            self._foreign_dict = res.copy()
        return self._foreign_dict

    def create_for_models(self,*hosters):
        create_dict={}
        for hoster in hosters:
            if isinstance(hoster,str):
                app_name,model_name,object_id = hoster.split('-')
                hoster_type = ContentType.objects.get(app_label=app_name, model=model_name)
                hoster = hoster_type.get_object_for_this_type(pk=object_id)
            else:
                app_name,model_name = hoster._meta.app_label, hoster._meta.model_name
            key = self.foreign_model_dict['%s-%s'%(app_name,model_name)]
            print('key',key)
            create_dict[key] = hoster
        return self.model(**create_dict)




