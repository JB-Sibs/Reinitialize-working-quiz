# forms.py
from django import forms
from .models import Quiz
from class_app.models import Course
from questions.models import Question, Answer

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name', 'course', 'no_of_questions', 'req_score_to_pass', 'period', 'attempts_allowed', 'time_limit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.HiddenInput(),
            'no_of_questions': forms.NumberInput(attrs={'class': 'form-control'}),
            'req_score_to_pass': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'score to pass'}),
            'period': forms.Select(choices=Quiz.PERIOD_CHOICES, attrs={'class': 'form-control'}),
            'attempts_allowed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of attempts allowed'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Time limit in minutes'}),
        }
    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'quiz']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the question'}),
            'quiz': forms.HiddenInput(),  # We will pass the quiz ID dynamically
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'correct', 'question']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the answer'}),
            'correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question': forms.HiddenInput(),
        }