
from people.models import Person
from rooms.models import Room, Style
from reservations.models import Reservation
import datetime


def initial(*args, **kwargs):
    
    if Style.objects.count() == 0:
        s1 = Style(name = 'green',  border_color = '4DB810', background_color = '7BD148', text_color = 'FFFFFF', shift = 0)
        s2 = Style(name = 'yellow', border_color = 'BDB634', background_color = 'FBE983', text_color = 'FFFFFF', shift = 1)
        s3 = Style(name = 'red',    border_color = 'A64232', background_color = 'F83A22', text_color = 'FFFFFF', shift = 2)
        s4 = Style(name = 'blue',   border_color = '2C70D1', background_color = '4986E7', text_color = 'FFFFFF', shift = 3)
        s1.save(); s2.save(); s3.save(); s4.save()
        r1 = Room(name = 'HG00.209', capacity = 12, pc_count = 2, style = s1)
        r2 = Room(name = 'HG00.212', capacity = 12, pc_count = 2, style = s2)
        r3 = Room(name = 'HG00.215', capacity = 12, pc_count = 2, style = s3)
        r4 = Room(name = 'HG00.217', capacity = 8 , pc_count = 2, style = s4)
        p = Person(email = 'mverleg@science.ru.nl', name = 'Mark Verleg')
        r1.save(); r2.save(); r3.save(); r4.save()
        p.save()
        Reservation(name = 'Test', person = p, room = r1, start = datetime.datetime(2013, 2, 13, 12, 30, 0), end = datetime.datetime(2013, 2, 13, 17, 30, 0)).save()
        Reservation(name = 'Test', person = p, room = r1, start = datetime.datetime(2013, 2, 13, 8, 30, 0),  end = datetime.datetime(2013, 2, 13, 12, 30, 0)).save()
        Reservation(name = 'Test', person = p, room = r2, start = datetime.datetime(2013, 2, 13, 12, 30, 0), end = datetime.datetime(2013, 2, 13, 13, 30, 0)).save()
        Reservation(name = 'Test', person = p, room = r3, start = datetime.datetime(2013, 2, 13, 12, 30, 0), end = datetime.datetime(2013, 2, 13, 15, 30, 0)).save()
        Reservation(name = 'Test', person = p, room = r4, start = datetime.datetime(2013, 2, 13, 10, 30, 0), end = datetime.datetime(2013, 2, 13, 13, 30, 0)).save()
        Reservation(name = 'Test', person = p, room = r1, start = datetime.datetime(2013, 2, 14, 10, 30, 0), end = datetime.datetime(2013, 2, 14, 15, 30, 0)).save()
        Reservation(name = 'Test', person = p, room = r3, start = datetime.datetime(2013, 2, 14, 12, 30, 0), end = datetime.datetime(2013, 2, 14, 13, 30, 0)).save()
        Reservation(name = 'Test', person = p, room = r4, start = datetime.datetime(2013, 2, 14, 12, 30, 0), end = datetime.datetime(2013, 2, 14, 15, 30, 0)).save()
        print 'POST_SYNCDB'


