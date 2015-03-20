
from django import forms


class TimeForm(forms.Form):
	time = forms.TimeField(input_formats = ['%H:%M', ], widget = forms.TimeInput(attrs={'class': 'timepicker'}))


class KostenplaatsForm(forms.Form):
	kostenplaatsnummer = forms.CharField(min_length = 6, max_length = 20, required = True)
	relatie = forms.CharField(max_length = 64, initial = 'OWC - Library of science (Zaalwacht)')
	type_werk = forms.CharField(max_length = 64, initial = 'Loon normale uren 100%')


