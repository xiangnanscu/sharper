from django.conf.urls import patterns, url


urlpatterns = patterns('accounts.views',
    

    url(r'^login/$', 
        'login',
        {'template_name': 'accounts/login.html',},
        name='login'),
    url(r'^logout/$', 
        'logout',
        name='logout'),
    url(r'^register/$', 
        'register',
        {'template_name': 'accounts/register.html'},
        name='register'),
    url(r'^register/complete/$', 
        'register_complete',
        {'template_name': 'accounts/register_complete.html'},
        name='register_complete'),
    url(r'^activate/(?P<activation_key>[a-f0-9]{40})/$', 
        'activate',
        {'template_name': 'accounts/activate_fail.html'}, 
        name='activate'),
    url(r'^activate/complete/$', 
        'activate_complete',
        {'template_name': 'accounts/activate_complete.html'},
        name='activate_complete'),

    url(r'^password_change/$', 
        'password_change',
        {'template_name': 'accounts/password_change_form.html'},
        name='password_change'),
    url(r'^password_change/done/$', 
        'password_change_done',
        {'template_name': 'accounts/password_change_done.html'},
        name='password_change_done'),

    url(r'^password_reset/$', 
        'password_reset',
        {'template_name': 'accounts/password_reset_form.html',
        'email_template_name':'accounts/password_reset_email.html',
        'subject_template_name':'accounts/password_reset_subject.txt',},
        name='password_reset'),
    url(r'^password_reset/done/$', 
        'password_reset_done',
        {'template_name': 'accounts/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm',
        {'template_name': 'accounts/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^password_reset/complete/$', 
        'password_reset_complete',
        {'template_name': 'accounts/password_reset_complete.html'},
        name='password_reset_complete'),
 )
 
urlpatterns += patterns('accounts.views',
    url(r'^$',
        'list',
        {'template_name':'accounts/users.html'},
        name='list'),
    url(r'^(?P<user_pk>\d+)/$',
        'profile',
        {'template_name':'accounts/profile.html'},
        name='profile'),
    url(r'^(?P<user_pk>\d+)/(?P<tab>\w+)/$',
        'profile',
        {'template_name':'accounts/profile.html'},
        name='profile_tab'),

    url(r'^(?P<user_pk>\d+)/edit$',
        'profile_edit',
        {'template_name': 'accounts/profile_edit.html'},
        name='profile_edit'), 
    )