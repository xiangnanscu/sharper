import datetime
import hashlib
import random
import re
from django.conf import settings
from django.db import models
from django.core import validators
from django.core.mail import send_mail
from django.contrib.sites.models import get_current_site
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now

# from django.contrib.contenttypes import generic
# from notices.models import Notice
# from mails.models import Mail
# from tags.models import Tag
# from flags.models import Flag
# from votes.models import Vote

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class UserManager(BaseUserManager):
    def _create_user(self,
        email,
        username,
        password,
        is_active,
        is_staff, 
        is_superuser,        
        **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """

        now = timezone.now()
        if not email or not username:
            raise ValueError(_('Users must have an email address and a username'))
        email = self.normalize_email(email)
        user = self.model(email=email,
            username=username,
            is_active=is_active,
            is_staff=is_staff, 
            is_superuser=is_superuser,
            last_login=now, 
            date_joined=now, 
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)  
        return user

    def create_user(self, email,username, password,**extra_fields):
        "创建普通用户"
        user = self._create_user(email, username, password,False,False,False,**extra_fields)
        user.set_and_send_activation_key()
        return user

    def create_superuser(self, email,username, password,**extra_fields):
        "创建超级用户"
        return self._create_user(email, username, password,True,True,True,**extra_fields)

    def get_by_natural_key(self, username):
        try:
            user = self.get(**{self.model.USERNAME_FIELD: username})
        except self.model.DoesNotExist:
            user = self.get(**{self.model.USERNAME_FIELD_OTHER: username})
        return user

    def activate_user(self, activation_key):
        """
        根据activation_key尝试激活对应的用户
        """
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.is_active = True
                user.activation_key = settings.ACTIVATED
                user.save(using=self._db)
                return user
        return False

    def delete_expired_users(self):
        """
        删除所有过期且未激活的用户,建议定期运行        
        """
        for user in self.all():
            if user.activation_key_expired() and (not user.is_active):
                user.delete()        

@python_2_unicode_compatible
class User(AbstractBaseUser, PermissionsMixin):

    objects = UserManager()
    class Meta:
        ordering = ['-reputation']    
        
    USERNAME_FIELD = 'email'
    USERNAME_FIELD_OTHER = 'username'
    REQUIRED_FIELDS = ['username']
    
    email = models.EmailField(
        verbose_name=_('邮箱'),
        max_length=75,
        unique=True,
        db_index=True,
        
        )
    username = models.CharField(
        verbose_name=_('昵称'),
        max_length=10, 
        unique=True,
        help_text=_('10个以内汉字、字母、数字或者.+-_'),
        validators=[validators.RegexValidator(
            regex=re.compile('^[\w.+-]+$'), 
            message=_('请输入一个有效用户名'), 
            code='invalid')],
        )
    is_active = models.BooleanField(
        verbose_name=_('active'), 
        default=False, 
        help_text=_('用户能否登录网站'),
        
        )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'), 
        default=False,
        help_text=_('用户能否登录管理网站'),
        
        )
    date_joined = models.DateTimeField(_('date joined'), 
        default=timezone.now,
        
        )
    activation_key = models.CharField(_('activation key'), 
        max_length=40, 
        default=settings.ACTIVATED,
        
        )
    location = models.CharField(max_length=10,blank=True,verbose_name=_('城市'))  
    avatar = models.ImageField(upload_to='avatar',null=True,blank=True,verbose_name=_('头像'))  
    description = models.TextField(max_length=200,blank=True,verbose_name=_('个人说明'))  
    signature = models.CharField(max_length=30,blank=True,verbose_name=_('个人签名'))  
    reputation = models.SmallIntegerField(default=1,verbose_name=_('声望'),)  
    viewed = models.PositiveIntegerField(default=0,verbose_name=_('被浏览'),)  

    def __str__(self):
        return self.username

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return settings.DEFAULT_AVATAR_URL

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def set_and_send_activation_key(
        self,
        request=None,
        subject_template_name='accounts/activation_email_subject.txt',
        email_template_name='accounts/activation_email.txt',
        ):
        """生成,保存并发送密匙"""

        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        activation_key = hashlib.sha1((salt+self.username).encode('utf-8')).hexdigest()
        self.activation_key = activation_key
        self.save(update_fields=['activation_key'])

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        c = {
            'protocol': 'https' if request.is_secure() else 'http',
            'domain': domain,
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site_name': site_name,}
        subject = render_to_string(subject_template_name,c)
        subject = ''.join(subject.splitlines())
        message = render_to_string(email_template_name,c)
        self.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    def activation_key_expired(self):
        "验证密匙是否失效,密匙等于默认值视为失效(即用户是管理员或者已激活)"
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == settings.ACTIVATED or \
               (self.date_joined + expiration_date <= datetime_now())

    #不知道这一句有什么用,先不用
    #activation_key_expired.boolean = True

    @property
    def url(self):
        return reverse('users:profile', args=[str(self.pk)])

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_profile(self):
        """
        官方说这是一个过时的方法.故不写
        """
        raise NotImplementedError


