
from django.contrib.admin import site
from rooms.models import Room, Style


site.register(Room)
site.register(Style)

