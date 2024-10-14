from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password

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


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']


class EnrollmentFormAdmin(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Select Course")
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")

    class Meta:
        model = Enrollment
        fields = ['course', 'user']

    # Override the clean method to prevent duplicate enrollments
    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        user = cleaned_data.get('user')

        # Check if the user is already enrolled in the course
        if Enrollment.objects.filter(course=course, user=user).exists():
            raise forms.ValidationError(f"{user.username} is already enrolled in {course.name}.")

        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Make email required

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_professor', 'is_student', 'is_admin')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("An account with this username already exists.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the user roles based on form input
        user.is_professor = self.cleaned_data.get('is_professor')
        user.is_student = self.cleaned_data.get('is_student')
        user.is_admin = self.cleaned_data.get('is_admin')
        if commit:
            user.save()
        return user


class AdminPasswordChangeForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')

        # Check if any existing user already has this password
        for user in User.objects.all():
            if check_password(new_password, user.password):
                raise forms.ValidationError("This password is already in use by another user.")

        return new_password

    def save(self):
        # Get the selected user
        user = self.cleaned_data['user']

        # Set and save the new password for the user
        new_password = self.cleaned_data['new_password']
        user.set_password(new_password)  # This handles hashing
        user.save()

        return user