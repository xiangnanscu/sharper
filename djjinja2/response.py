from django.template.response import TemplateResponse as DjangoTemplateResponse
from django.utils import six

from djjinja2 import loader


class TemplateResponse(DjangoTemplateResponse):
    def resolve_template(self, template):
        if isinstance(template, (list, tuple)):
            return loader.select_template(template, self._request.path)
        elif isinstance(template, six.string_types):
            return loader.get_template(template, self._request.path)
        else:
            return template
