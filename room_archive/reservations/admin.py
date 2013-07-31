
from django.contrib.admin import site
from reservations.models import Reservation

site.register(Reservation)
