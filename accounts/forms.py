from django import forms
from education.models import Group, Course
from authentication.models import CustomUser


class GroupForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='student'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = Group
        fields = ('name', 'course', 'teacher', 'level', 'teacher_share', 'students')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Group name'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'teacher_share': forms.Select(choices=[
                (0.30, '30%'), (0.35, '35%'), (0.40, '40%'), (0.45, '45%'), (0.50, '50%'),
            ], attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['students'].queryset = CustomUser.objects.filter(role='student')
            self.fields['students'].initial = self.instance.students.all()
        self.fields['teacher'].queryset = CustomUser.objects.filter(role='teacher')


class ReplenishBalanceForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


class StudentGroupsForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'duration', 'description', 'lesson_price')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lesson_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }