from django.conf.urls import patterns, url  
from answers import views

urlpatterns = patterns('answers.views',  
    url(r'^create/(?P<hoster_pk>\d+)/$', views.AnswerCreate.as_view(),name='AnswerCreate'),
    url(r'^(?P<pk>\d+)/update/$', views.AnswerUpdate.as_view(),name='AnswerUpdate'),
    url(r'^comments/create/(?P<hoster_pk>\d+)/$', views.CommentCreate.as_view(),name='CommentCreate'),
    url(r'^comments/(?P<pk>\d+)/update/$', views.CommentUpdate.as_view(),name='CommentUpdate'),    
    )
