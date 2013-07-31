
from django import forms


class TimeForm(forms.Form):
    time = forms.TimeField(input_formats = ['%H:%M', ], widget = forms.TimeInput(attrs={'class': 'timepicker'}))
    


