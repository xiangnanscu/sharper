from django.conf.urls import patterns, url  
from django.views.decorators.cache import cache_page

from tools import showbug
from questions import views

urlpatterns = patterns('questions.views',  
	url(r'^test/(\d+)/$', cache_page(60 * 15)(views.test),name='test'),
    url(r'^$', cache_page(60 * 15*10**-2)(views.QuestionList.as_view()),name='QuestionList'),
    url(r'^create/$', views.QuestionCreate.as_view(),name='QuestionCreate'),
    url(r'^(?P<pk>\d+)/update/$', views.QuestionUpdate.as_view(),name='QuestionUpdate'),
    url(r'^comments/create/(?P<hoster_pk>\d+)/$', showbug(views.CommentCreate.as_view()),name='CommentCreate'),
    url(r'^comments/(?P<pk>\d+)/update/$', views.CommentUpdate.as_view(),name='CommentUpdate'),
    url(r'^(?P<pk>\d+)/detail/$', views.QuestionDetail.as_view(),name='QuestionDetail'),
    ) 
