from django.conf.urls import patterns, url  


urlpatterns = patterns('common.views',  
    url(r'^vote/$', 'vote',name='vote'),   
    url(r'^favor/$', 'favor',name='favor'),  
    url(r'^accept/$', 'accept',name='accept'),
    # url(r'^comment/$', 'comment',name='comment'),
    )
