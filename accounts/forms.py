from __future__ import unicode_literals
import warnings
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.forms.util import flatatt
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_bytes
from django.utils.html import format_html, format_html_join
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX, identify_hasher
from django.contrib.sites.models import get_current_site

User = get_user_model()

class ProfileForm(forms.ModelForm): 
    class Meta:
        model = User
        fields = ['avatar','location', 'description', 'signature']
        widgets = {
          'description': forms.Textarea(attrs={'rows':15,'class':'form-control'}),
          'location': forms.TextInput(attrs={'class':'form-control'}),
          'signature': forms.TextInput(attrs={'class':'form-control'}),
          #'avatar': forms.FileInput(attrs={'style':'width:433px;'}),
        }
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    class Meta:
        model = User
        fields = ('email','username',) 

    error_messages = {
        'email_duplicate': _("该邮箱已存在"),
        'username_duplicate': _("该昵称已存在"),
        'password_too_short':_("密码至少6位数"),
    }
    email=forms.EmailField(label="邮箱", 
        max_length=75,
        widget=forms.TextInput(attrs={'placeholder':'用于接收激活邮件,完成注册', 'class':'form-control'}),
        )
    username=forms.CharField(label="昵称",
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder':'中英文均可,最长10个字符', 'class':'form-control'}),
        )
    password=forms.CharField(label="密码", 
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder':'至少6个字符,区分大小写', 'class':'form-control'}),
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['email_duplicate'],
            code='email_duplicate',
        )

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['username_duplicate'],
            code='username_duplicate',
        )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password)<6:
            raise forms.ValidationError(
            self.error_messages['password_too_short'],
            code='password_too_short',
        )
        return password

    def save(self, commit=True, request=None,):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        user.set_and_send_activation_key(request=request)
        return user

class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(
        label=_('账号'), 
        max_length=75,
		widget=forms.TextInput(attrs={'placeholder':'昵称或邮箱', 'class':'form-control'})
        )
    password = forms.CharField(
        label=_("密码"), 
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder':'', 'class':'form-control'}),
        )
    error_messages = {
        'invalid_login': "账号或密码错误",
        'inactive': _("该账号未激活,无法登录"),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        
        self.username_field = User._meta.get_field(User.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)
        if self.fields['password'].label is None:
            self.fields['password'].label = User._meta.get_field('password').verbose_name

    def clean(self):
        username = self.cleaned_data.get('username') 
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(username=username,password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data

    def check_for_test_cookie(self):
        warnings.warn("check_for_test_cookie is deprecated; ensure your login "
                "view is CSRF-protected.", DeprecationWarning)

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial["password"]

class PasswordResetForm(forms.Form):
    "通过邮箱找回密码的表单"
    email = forms.EmailField(label=_("Email"), max_length=75)

    def save(self, 
             domain_override=None,
             subject_template_name='accounts/password_reset_subject.txt',
             email_template_name='accounts/password_reset_email.html',
             token_generator=default_token_generator,
             use_https=False, 
             from_email=None, 
             request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        
        email = self.cleaned_data["email"]
        active_users = User._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                }
            subject = loader.render_to_string(subject_template_name, c)
            subject = ''.join(subject.splitlines())
            message = loader.render_to_string(email_template_name, c)
            user.email_user(subject, message, from_email)

class SetPasswordForm(forms.Form):
    """
    直接填写2个密码,提交后即可为该用户重设密码.
    A form that lets a user change set his/her password without entering the
    old password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_too_short':_("密码至少6位数"),
    }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        if len(password2)<6:
            raise forms.ValidationError(
            self.error_messages['password_too_short'],
            code='password_too_short',
        )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

class PasswordChangeForm(SetPasswordForm):
    """
    通过旧密码更改密码
    继承了密码重设的表格,密码更改表格相当于只是多了一个旧密码框.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Your old password was entered incorrectly. "
                                "Please enter it again."),
    })
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

PasswordChangeForm.base_fields = SortedDict([
    (k, PasswordChangeForm.base_fields[k])
    for k in ['old_password', 'new_password1', 'new_password2']
])

class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"),
                                widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()
        return self.user

    def _get_changed_data(self):
        data = super(AdminPasswordChangeForm, self).changed_data
        for name in self.fields.keys():
            if name not in data:
                return []
        return ['password']
    changed_data = property(_get_changed_data)

