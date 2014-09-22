import datetime
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect, QueryDict, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
#from django.template.response import TemplateResponse
from djjinja2.response import TemplateResponse
from django.utils.http import base36_to_int, is_safe_url, urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import ugettext as _
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.shortcuts import resolve_url
from django.utils.encoding import force_bytes, force_text
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (REDIRECT_FIELD_NAME, authenticate, 
    get_user_model, login as auth_login, logout as auth_logout)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.utils.timezone import now as datetime_now
from django.contrib.auth.decorators import login_required

from .forms import (UserCreationForm, AuthenticationForm,
    PasswordResetForm, SetPasswordForm, PasswordChangeForm, ProfileForm)
from tools import *

User = get_user_model()

def list(request,
    template_name,):
    pass

def profile(request,
    template_name,):
    pass
@login_required
def mail(request,
    template_name,):
    pass

@login_required
def notice(request,
    template_name,):
    user=request.user
    items=user.notice_set.all()
    return TemplateResponse(request, template_name, locals(),)

@login_required
def notice_redi(request,notice_pk):
    items=Notice.objects.filter(pk=notice_pk)
    if items:
        redi=items[0].url
        items.delete()   
    else:
        redi='/'
    return HttpResponseRedirect(redi)

def users(request,
            template_name,
            tab='reputation',
            page='1',
            pagesize=16,
            tab_dic={
            'reputation':'-reputation',
            'newusers':'-date_joined',
            },
    ):
    page=int(page)
    _users=User.objects.all()
    body_class='users-page new-topbar'
    header_type='users'
    viewname = 'users:users_tab'
    pagination_kwargs={'tab':tab,}
    _items=_users if tab=='reputation' else _users.order_by(tab_dic[tab])
    page_list,item_list = paginator(
        page=page,
        items=_items,
        pagesize=pagesize,
        width=2,
        )
    users_list=[item_list[a:a+4] for a in range(0,len(item_list),4)]
    return TemplateResponse(request, template_name, locals(),)

def profile(request,
    template_name,
    user_pk,
    tab='summary',
    sort='votes',
    page='1',
    pagesize=10,
    sort_dic={
    'newest':'-create_time',
    'active':'-edit_time',
    'votes':'-votes',
    'views':'-viewed',},
    ):
    page=int(page)
    header_type='users'
    anchor='tab-top' #用于控制页码视图的锚
    pagination_kwargs={'sort':sort,'tab':tab,'user_pk':user_pk,}
    profile_user = get_object_or_404(User,pk=user_pk)
    request_user = request.user
    display_username ='你' if profile_user==request_user else '该用户'
    member_age = datetime_now()-profile_user.date_joined
    if request_user!=profile_user:
        profile_user.viewed += 1
        profile_user.save(update_fields=['viewed']) 
    profile_answers = profile_user.questions_answer_creater.all()
    profile_questions = profile_user.question_set.all()
    viewname = 'users:profile_tab_sort_page'
    if tab=='questions':
        if sort=='votes':
            items=sorted(profile_questions,key=lambda a:a.score,reverse=True)
        else:
            items=profile_questions.order_by(sort_dic[sort])
        page_list,item_list = paginator(
            page=page,
            items=items,
            pagesize=pagesize,
            width=2
            )
    elif tab=='answers':
        if sort=='votes':
            items=sorted(profile_answers,key=lambda a:a.score,reverse=True)
        else:
            items=profile_answers.order_by(sort_dic[sort])
        page_list,item_list = paginator(
            page=page,
            items=items,
            pagesize=pagesize,
            width=2
            )
    return TemplateResponse(request, template_name, locals(),)


def profile_edit(request,
    template_name, 
    user_pk,
    edit_form=ProfileForm,
    ):
    header_type='users'
    request_user = request.user
    if not request_user.is_authenticated():
        return HttpResponseRedirect(reverse('accounts:login'),)
    if request_user.pk!=int(user_pk):
        raise Http404
    if request.method == 'POST':
        form = edit_form(data=request.POST, files=request.FILES,instance=request_user)
        if form.is_valid():
            updated_profile = form.save() 
            return HttpResponseRedirect(
                reverse('users:profile',kwargs={'user_pk':user_pk,}),
                )
    else:
        form = edit_form(instance=request_user)
    return TemplateResponse(request, template_name, locals(),)

@sensitive_post_parameters()
@never_cache
def register(request,template_name):
    if request.user.is_authenticated():
    	return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save(request=request)
            return HttpResponseRedirect(reverse('accounts:register_complete'))
    else:
        form = UserCreationForm()    
    context = {
    'form': form,
    }
    return TemplateResponse(request, template_name, context,)

def register_complete(request,template_name):
    return TemplateResponse(request, template_name,{})
    # return render_to_response(
    #     template_name,
    #     dict(user=request.user),
    # )

def activate(request,activation_key,template_name):
    user = User.objects.activate_user(activation_key)
    if user:
        return HttpResponseRedirect(reverse('accounts:activate_complete'))
    return render_to_response(
        template_name,
        dict(user=request.user),
    )

def activate_complete(request,template_name):
    return render_to_response(
        template_name,
        dict(user=request.user),
    )

@sensitive_post_parameters()
@csrf_protect 
@never_cache
def login(request,
    template_name='accounts/login.html',
    redirect_field_name="next",
    authentication_form=AuthenticationForm,
    extra_context=None,
    current_app=None,
    ):
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            #'next'取不到值导致redirect_to为空字符串时,就要这样,否则会无限循环.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redirect_to)
            #return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form=authentication_form()
    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def password_reset(request, 
                   template_name,
                   email_template_name,
                   subject_template_name,
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('accounts:password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'user':request.user,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def password_reset_done(request,
                        template_name,
                        current_app=None, 
                        extra_context=None):
    context = dict(user=request.user)
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request,template_name, uidb64=None, token=None,                           
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  
    if post_reset_redirect is None:
        post_reset_redirect = reverse('accounts:password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
        'user':request.user,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def password_reset_complete(request,
                            template_name,
                            current_app=None, extra_context=None):
    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'user':request.user,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

@sensitive_post_parameters()
@login_required
def password_change(request,
                    template_name,
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('accounts:password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'user':request.user,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
@login_required
def password_change_done(request,
                         template_name,
                         current_app=None, extra_context=None):
    context = {'user':request.user,}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)