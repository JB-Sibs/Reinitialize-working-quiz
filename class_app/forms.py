from django import forms
from django.forms import ModelForm
from .models import *

class Announcementform(ModelForm):
    class Meta:
        model = Announcement
        fields = ('title','content',)

class Materialsform(ModelForm):
    class Meta:
        model = Materials
        fields = ('title', 'content',)


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ['student', 'exam_name', 'score', 'total_items','period']
        widgets = {
            'period': forms.Select(choices=Grade.PERIOD_CHOICES),
        }

    from django import forms
    from .models import Grade

    class GradeForm(forms.ModelForm):
        class Meta:
            model = Grade
            fields = ['user', 'quiz', 'score', 'passed', 'period']  # Added 'period' field
            widgets = {
                'period': forms.Select(choices=Grade.PERIOD_CHOICES),
            }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['user']  # Only selecting the student to enroll
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)
        # Limit the choices to users who are students
        self.fields['user'].queryset = User.objects.filter(is_student=True)
