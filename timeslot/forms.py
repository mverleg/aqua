
from django import forms
from timeslot.models import Roster


class CreateRosterForm(forms.ModelForm):
    start = forms.DateField(input_formats = ['%Y-%m-%d', ], widget = forms.DateInput(attrs={'class': 'datepicker'}))
    end =   forms.DateField(input_formats = ['%Y-%m-%d', ], widget = forms.DateInput(attrs={'class': 'datepicker'}))
    
    class Meta:
        model = Roster
        exclude = ('state', )
    

class TemplateRosterForm(forms.Form):
    roster = forms.ModelChoiceField(queryset=Roster.objects.all(), required = False)
    

class TimeSlotForm(forms.Form):
    date =  forms.DateField(input_formats = ['%Y-%m-%d', ], widget = forms.DateInput(attrs={'class': 'datepicker'}))
    start = forms.TimeField(input_formats = ['%H:%M', ], widget = forms.TimeInput(attrs={'class': 'timepicker'}))
    end =   forms.TimeField(input_formats = ['%H:%M', ], widget = forms.TimeInput(attrs={'class': 'timepicker'}))
    people = forms.IntegerField(initial = 1)
    
    def clean(self):
        super(TimeSlotForm, self).clean()
        if self.cleaned_data['start'] >= self.cleaned_data['end']:
            raise forms.ValidationError('Start time should be before the end time')
        if not 1 <= self.cleaned_data['people'] <= 10:
            raise forms.ValidationError('Number of people should be between 1 and 10 (inclusive)')
        return self.cleaned_data


