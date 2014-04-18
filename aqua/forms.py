
from django.forms import models
from django import forms
from aqua.models import AquaUser


class UserForm(models.ModelForm):
    
    birthday = forms.DateField(input_formats = ['%Y-%m-%d', ], widget = forms.DateInput(attrs={'class': 'datepicker'}), required = False)
    
    class Meta:
        fields = ['first_name', 'last_name', 'birthday']
        model = AquaUser


