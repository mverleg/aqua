
from aqua.functions.initial import initial
from django.db.models.signals import post_syncdb


post_syncdb.connect(initial)
