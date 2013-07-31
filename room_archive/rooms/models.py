
from django.db import models
from colorfield.fields import ColorField


class Style(models.Model):
    
    name = models.CharField(max_length = 32, unique = True)
    background_color = ColorField(default='000000')
    border_color = ColorField(default='000000')
    text_color = ColorField(default='ffffff')
    shift = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return '%s' % self.name
    
    @property
    def left_shift(self):
        return (self.shift % 5) * 10;
    
    @property
    def right_shift(self):
        return 50 - self.left_shift
    
    def zindex(self):
        return 10-self.shift;

class Room(models.Model):
    
    name = models.CharField(max_length = 32, unique = True)
    special = models.TextField(blank = True, null = True)
    capacity = models.PositiveIntegerField()
    pc_count = models.PositiveIntegerField()
    style = models.ForeignKey(Style)
    
    def __unicode__(self):
        return '%s' % self.name

