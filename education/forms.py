from django import forms
from .models import Lesson, Homework, Submission


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'context', 'video', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lesson title'}),
            'context': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Lesson info...'}),
            'video': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ('task', 'file')
        widgets = {
            'task': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Task description...'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('context', 'file')
        widgets = {
            'context': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your answer...'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('points',)
        widgets = {
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }