from django.conf import settings
from importlib import import_module
# Create your models here.
for m in settings.NEWT_CONFIG['ADAPTERS']['AUTH']['models']:
    module = import_module(m['module'])
    locals()[m['name']] = getattr(module, m['name'])