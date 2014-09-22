from django.conf.urls import patterns, url  


urlpatterns = patterns('blogs.views',  

    url(r'^$', 'list',name='list'),
    url(r'^create/$', 'create',name='create'),
    url(r'^edit/(?P<blog_pk>\d+)/$', 'edit',name='edit'),
    #url(r'^create-comment/$', 'create_comment',name='create_comment'),
    )
