from django.conf import settings
from importlib import import_module

for m in settings.NEWT_CONFIG['ADAPTERS']['ACCOUNT']['models']:
    module = import_module(m['module'])
    locals()[m['name']] = getattr(module, m['name'])