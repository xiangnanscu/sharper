from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.template.loader import BaseLoader, find_template_loader, make_origin, get_template_from_string
from django.template.loaders.app_directories import app_template_dirs

from djjinja2 import custom
import jinja2

template_source_loaders = None

ALL_PATH = settings.TEMPLATE_DIRS + app_template_dirs

class jinja2Template(jinja2.Template):
    def render(self, context):
        # flatten the Django Context into a single dictionary.
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        return super(jinja2Template, self).render(context_dict)

class Loader(BaseLoader):
    "jinja2模板引擎的loader"
    is_usable = True
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ALL_PATH))
    env.template_class = jinja2Template
    env.globals.update(custom.dicts)
    env.filters.update(custom.filters) 

    def load_template(self, template_name, template_dirs=None):
        try:
            template = self.env.get_template(template_name)
            return template, template.filename
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)

def find_template(name, dirs=None, url=None):
    # url是request.path, 例如/admin/,或者/users/1/之类的字符串
    global template_source_loaders
    tds=settings.TEMPLATE_LOADERS
    if url is not None and settings.IS_DJANGO_TEMPLATE_PATH.search(url):
        tds=[t for t in tds if t.startswith('django.template.loaders.')]
    else:
        tds=[t for t in tds if not t.startswith('django.template.loaders.')]
    if template_source_loaders is None:
        loaders = []
        for loader_name in tds:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        template_source_loaders = tuple(loaders)
    #print('template_source_loaders',template_source_loaders)
    for loader in template_source_loaders:
        try:
            source, display_name = loader(name, dirs)
            return (source, make_origin(display_name, loader, name, dirs))
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)

def get_template(template_name, url=None):
    template, origin = find_template(template_name, url=url)
    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return template

def select_template(template_name_list, url=None):
    if not template_name_list:
        raise TemplateDoesNotExist("No template names provided")
    not_found = []
    for template_name in template_name_list:
        try:
            return get_template(template_name, url=url)
        except TemplateDoesNotExist as e:
            if e.args[0] not in not_found:
                not_found.append(e.args[0])
            continue
    # If we get here, none of the templates could be loaded
    raise TemplateDoesNotExist(', '.join(not_found))
