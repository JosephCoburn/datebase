from django.forms import ModelForm
from .models import Rdv, Match, Match_notes
from django import forms

class RdvForm(ModelForm):
    class Meta:
        model = Rdv
        rdv_time = forms.TimeField(input_formats=['%I:%M %p'],      widget=forms.TimeInput)
        fields = ['match', 'date', 'rdv_time', 'what', 'where']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RdvForm, self).__init__(*args, **kwargs)
        self.fields['match'].queryset = Match.objects.filter(user=user)



class NotesForm(ModelForm):
    class Meta:
        model = Match_notes
        fields = ['notes']

