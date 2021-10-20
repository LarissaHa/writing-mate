from django import forms

#from .widgets import XDSoftDateTimePickerInput
from .models import Log, Project

#class DateInput(forms.DateInput):
#    input_type = 'date'


class LogEditForm(forms.ModelForm):
    #date = forms.DateField(input_formats=['%Y-%m-%d'], widget=XDSoftDateTimePickerInput())
    
    class Meta:
        model = Log
        fields = ('count', 'date', 'time', 'note')

class LogForm(forms.ModelForm):
    #date = forms.DateField(input_formats=['%Y-%m-%d'], widget=XDSoftDateTimePickerInput())
    
    class Meta:
        model = Log
        fields = ('project', 'count', 'date', 'time', 'note')
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.filter(user=request.user).order_by("-created_at")


class WordcountForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = ('count',)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'title', 
            'subtitle', 
            'goal',
            'unit', 
            'deadline',
            'status', 
            'topic', 
            'type', 
            'synopsis', 
            'excerpt', 
            'pinterest', 
            'spotify'
        )