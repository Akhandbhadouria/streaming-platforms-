import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Aura.settings')
import django
django.setup()

from django.template.context import BaseContext
import copy

c = BaseContext({"a": 1})
print("Original:", c)
c_copy = copy.copy(c)
print("Copy:", c_copy)
print("Success!")
