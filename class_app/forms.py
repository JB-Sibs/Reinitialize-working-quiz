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
        fields = ['student', 'exam_name', 'score', 'total_items']