from django import forms

from .models import Log, Project

class LogForm(forms.ModelForm):

    class Meta:
         model = Log
         fields = ('project', 'count', 'date', 'time', 'note')


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'title', 
            'subtitle', 
            'slug', 
            'goal', 
            'unit', 
            'status', 
            'topic', 
            'type', 
            'synopsis', 
            'excerpt', 
            'pinterest', 
            'spotify'
        )