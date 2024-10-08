# forms.py
from django import forms
from .models import Quiz
from class_app.models import Course
from questions.models import Question, Answer

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name', 'course', 'topic', 'no_of_questions', 'time', 'req_score_to_pass']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.HiddenInput(),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'no_of_questions': forms.NumberInput(attrs={'class': 'form-control'}),
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'duration of the quiz in minutes'}),
            'req_score_to_pass': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'score to pass'}),
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