from django.conf.urls import patterns, url  
from replys import views

urlpatterns = patterns('replys.views',  
    url(r'^create/(?P<hoster_pk>\d+)/$', views.ReplyCreate.as_view(),name='ReplyCreate'),
    url(r'^(?P<pk>\d+)/update/$', views.ReplyUpdate.as_view(),name='ReplyUpdate'),
    url(r'^comments/create/(?P<hoster_pk>\d+)/$', views.CommentCreate.as_view(),name='CommentCreate'),
    url(r'^comments/(?P<pk>\d+)/update/$', views.CommentUpdate.as_view(),name='CommentUpdate'),    
    )
