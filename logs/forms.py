from django import forms

from .models import Log, Project

class LogForm(forms.ModelForm):
    
    class Meta:
        model = Log
        fields = ('project', 'count', 'date', 'time', 'note')
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.filter(user=request.user).order_by("-created_at")


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