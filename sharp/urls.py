from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^test/$', 'sharp.views.test', name='test'),
    url(r'^$', 'sharp.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^common/', include('common.urls',namespace='common')), 
    url(r'^accounts/', include('accounts.urls',namespace='accounts')), 
    url(r'^questions/', include('questions.urls',namespace='questions')),
    url(r'^answers/', include('answers.urls',namespace='answers')),
    url(r'^blogs/', include('blogs.urls',namespace='blogs')),
    url(r'^topics/', include('topics.urls',namespace='topics')),
    url(r'^replys/', include('replys.urls',namespace='replys')),  
     
)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT )