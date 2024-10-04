from django import forms
from django.forms import ModelForm
from .models import Announcement, Materials

class Announcementform(ModelForm):
    class Meta:
        model = Announcement
        fields = ('title','content',)

class Materialsform(ModelForm):
    class Meta:
        model = Materials
        fields = ('title', 'content',)