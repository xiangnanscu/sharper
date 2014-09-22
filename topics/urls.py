from django.conf.urls import patterns, url  
from topics import views

urlpatterns = patterns('topics.views',  
	# url(r'^test/(\d+)/(\w+)/(?P<xxx>\w+)/$', 'test',name='test'),
    url(r'^$', views.TopicList.as_view(),name='TopicList'),
    url(r'^create/$', views.TopicCreate.as_view(),name='TopicCreate'),
    url(r'^(?P<pk>\d+)/update/$', views.TopicUpdate.as_view(),name='TopicUpdate'),
    url(r'^comments/create/(?P<hoster_pk>\d+)/$', views.CommentCreate.as_view(),name='CommentCreate'),
    url(r'^comments/(?P<pk>\d+)/update/$', views.CommentUpdate.as_view(),name='CommentUpdate'),
    url(r'^(?P<pk>\d+)/detail/$', views.TopicDetail.as_view(),name='TopicDetail'),
    )
