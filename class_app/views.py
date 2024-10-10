from django.contrib.auth import authenticate, login as auth_login, logout

from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import Announcementform, Materialsform, ExamResultForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from quizzes.models import Quiz  # Import the Quiz model




def home_view(request):
    instance = request.user
    query = Enrollment.objects.filter(user=instance)

    print(query.values('course__name'))
    context = {
        'query': query
    }
    return render(request, 'index.html', context)


def course_view(request, pk):
    # Fetch course object
    obj = Course.objects.get(pk=pk)

    # Filter related data based on course
    announcements = Announcement.objects.filter(course=obj)
    materials = Materials.objects.filter(course=obj)
    quizzes = Quiz.objects.filter(course=obj)
    # Fetch exam results for the current user and course
    exam_results = ExamResult.objects.filter(course=obj, student=request.user)
    exam_results_prof= ExamResult.objects.filter(course=obj)

    # Filter grades for quizzes related to this course, and get the quiz name and score
    results = Grade.objects.filter(quiz__course=obj, user=request.user).values('quiz__name', 'score')
    results_prof = Grade.objects.filter(quiz__course=obj).values('quiz__name', 'score')
    # Pass context to the template
    context = {
        'obj': obj,
        'announcements': announcements,
        'materials': materials,
        'quizzes': quizzes,
        'results': results,  # Passing both the quiz name and score
        'exam_results': exam_results,  # Passing the exam results to the template'
        'exam_results_prof': exam_results_prof,  # Passing the exam results to the template'
        'results_prof': results_prof,
    }

    return render(request, 'course.html', context)


def professor_dashboard(request):

    professor = request.user


    courses = Enrollment.objects.filter(user=professor)

    context = {
        'query': courses
    }

    return render(request, 'prof.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_student:
            auth_login(request, user)
            return redirect('class:home_view')  # Redirect to the home view after successful login
        elif user is not None and user.is_professor:
            auth_login(request, user)
            return redirect('class:professor_dashboard')
        else:
            messages.error(request, "Invalid username or password.")  # Add an error message
            return render(request, 'login.html')  # Render the login page again with an error
    else:
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('class:login')


def professor_required(user):
    if not user.is_professor:
        raise PermissionDenied
    return True

@login_required
@user_passes_test(professor_required)
def add_announcement(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = Announcementform(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.course = course  # Assign the course to the announcement
            announcement.save()
            return redirect('class:course_view', pk=course.pk)
    else:
        form = Announcementform()

    context = {
        'form': form,
        'course': course
    }
    return render(request, 'make_announcement.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('class:change_password')  # Redirect to a success page
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
@user_passes_test(professor_required)
def add_module(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = Materialsform(request.POST, request.FILES)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course  # Assign the course to the module
            module.created_by = request.user  # Set the creator as the logged-in professor
            module.save()
            return redirect('class:course_view', pk=course.pk)
    else:
        form = Materialsform()

    context = {
        'form': form,
        'course': course
    }
    return render(request, 'add_module.html', context)


def announcement_view(request, pk):
    obj = Course.objects.get(pk=pk)
    announcements = Announcement.objects.filter(course=obj)
    context = {
        'obj': obj,
        'announcements': announcements,
    }
    return render(request, 'announcement_view.html', context)


def add_exam_result_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if request.method == 'POST':
        form = ExamResultForm(request.POST)
        if form.is_valid():
            exam_result = form.save(commit=False)
            exam_result.professor = request.user  # Assign the logged-in professor
            exam_result.save()
            return redirect('class:course_view', pk=course.pk)  # Redirect to a page to see the results or course

    else:
        form = ExamResultForm()

    return render(request, 'add_exam_result.html', {'form': form, 'course': course})
