
from django import forms
from django.forms import models
from people.models import Person


class EmailForm(forms.Form):
    email = forms.EmailField()


class NameForm(models.ModelForm):
    
    class Meta:
        model = Person
        fields = ('name', )


