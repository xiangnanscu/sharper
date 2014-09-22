"""
Django settings for sharp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR,'media').replace('\\','/')+'/'
DEFAULT_AVATAR_URL = "/media/avatar/default.png"

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates').replace('\\','/'),
) 

#只要request.path能够匹配这个正则,则TEMPLATE_LOADERS只加载django自带的loader
#否则排除django自带的loader.
IS_DJANGO_TEMPLATE_PATH = re.compile('^/admin/')
PAGESIZE=5
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'djjinja2.loader.Loader',
)

#对POST请求(无论成功还是失败)进行次数累加的时间标准
CHECK_SECONDS=60
#比如某用户分别在1分钟,1.9分钟和2.8分钟发送了POST请求(即3次)
#那么如果他在3.8分钟之前再次GET表单并POST数据,就会被要求输入图形验证码.
ALLOW_TIMES=3

ACCOUNT_ACTIVATION_DAYS = 3
ACTIVATED = "ALREADY_ACTIVATED"
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'
PASSWORD_RESET_TIMEOUT_DAYS = 3
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'djangomaster@163.com'
EMAIL_HOST_USER = 'djangomaster@163.com'
EMAIL_HOST_PASSWORD = '```111'
EMAIL_USE_TLS = True


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n*xtz(2$#kgez9&s-v^b+nz6*(j*t)dx=40su3u@h*6@xk!rd#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'accounts',
    'questions',
    'common',
    'answers',
    'topics',
    'replys',
    'blogs',
)
 
MIDDLEWARE_CLASSES = (


    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sharp.middleware.AntiAttackMiddleware',
    
)


ROOT_URLCONF = 'sharp.urls'

WSGI_APPLICATION = 'sharp.wsgi.application'

 
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#静态文件目录
STATICFILES_DIRS = (  
    # Put strings here, like "/home/html/static" or "C:/www/django/static".  
    # Always use forward slashes, even on Windows.  
    # Don't forget to use absolute paths, not relative paths.  
    BASE_DIR+STATIC_URL,  
) 

ACCOUNT_ACTIVATION_DAYS = 3
ACTIVATED = "ALREADY_ACTIVATED"
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'
PASSWORD_RESET_TIMEOUT_DAYS = 3

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'djangomaster@163.com'
EMAIL_HOST_USER = 'djangomaster@163.com'
EMAIL_HOST_PASSWORD = '```111'

TAG_MAX_LENGTH = 7
TAG_MAX_COUNT = 7
TAG_SPLITER = ',;，；.。|'
TAG_SPLITER_REGEX=re.compile(r'[%s]'%TAG_SPLITER)
TAG_REGEX=re.compile(r'^((?:\w{1,%s}[%s]){1,%s})$'%(TAG_MAX_LENGTH,TAG_SPLITER,TAG_MAX_COUNT))

VALID_WORDS=re.compile(r'^[\s\w!"#$%&\'()*+,-./:;<=>?@\[\\\]^_`{|}~·—‘’“”…、。《》【】！（），：；？￥]+$')
COMMENTS_APP='comments'
COMMENTS_ALLOW_PROFANITIES = False
PROFANITIES_LIST = ['毛泽东','习近平']
# URL that handles the media served from MEDIA_ROOT.
# Examples: "http://example.com/media/", "http://media.example.com/"
# 默认值是空字符串,所以为了头像,这个必须要设置出来.
MEDIA_URL = '/media/'