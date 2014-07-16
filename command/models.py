from django.conf import settings
from importlib import import_module
import inspect

# Imports all the models from the class listed in settings.py
models_file = settings.NEWT_CONFIG['ADAPTERS']['COMMAND']['models']
if models_file:
    for name, model in inspect.getmembers(import_module(models_file), inspect.isclass):
        locals()[name] = model