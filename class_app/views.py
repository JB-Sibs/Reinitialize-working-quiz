from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login as auth_login, logout

from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Announcement

from .forms import Announcementform, Materialsform, ExamResultForm, EnrollmentForm, CourseForm, EnrollmentFormAdmin, \
    CustomUserCreationForm, AdminPasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from quizzes.models import Quiz  # Import the Quiz model


def admin_custom_view(request):
    courses = Course.objects.all()

    # Debugging output
    print(f"Courses fetched: {courses}")  # Check if courses are fetched

    context = {
        'courses': courses
    }

    return render(request, 'admin_dashboard.html', context)


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
    exam_results_prof = ExamResult.objects.filter(course=obj)

    # Filter grades for quizzes related to this course, and get the quiz name and score
    results = Grade.objects.filter(quiz__course=obj, user=request.user).values('quiz__name', 'score', 'period')
    results_prof = Grade.objects.filter(quiz__course=obj).values('user__username', 'quiz__name', 'score', 'passed','period')

    # Get grades filtered by period for the logged-in user
    prelim_final, prelim_transmuted, prelim_classification = get_prelim_grades(user=request.user, course=obj)
    midterm_final, midterm_transmuted, midterm_classification = get_midterm_grades(user=request.user, course=obj)
    final_final, final_transmuted, final_classification = get_final_grades(user=request.user, course=obj)

    total_final_grades = prelim_final + midterm_final + final_final
    final_grade_average = total_final_grades / 3

    # Create a list of materials with their types
    material_info = []
    for material in materials:
        file_extension = material.content.url.split('.')[-1].lower()  # Get the file extension
        material_info.append({
            'title': material.title,
            'url': material.content.url,
            'type': file_extension,
            'posted_on': material.created_on,
        })

    # Pass context to the template, including the grades
    context = {
        'obj': obj,
        'announcements': announcements,
        'materials': material_info,
        'quizzes': quizzes,
        'results': results,  # Passing both the quiz name and score
        'exam_results': exam_results,  # Passing the exam results to the template
        'exam_results_prof': exam_results_prof,  # Passing the exam results to the template
        'results_prof': results_prof,

        # Prelim grade information
        'prelim_final': prelim_final,
        'prelim_transmuted': prelim_transmuted,
        'prelim_classification': prelim_classification,

        # Midterm grade information
        'midterm_final': midterm_final,
        'midterm_transmuted': midterm_transmuted,
        'midterm_classification': midterm_classification,

        # Final grade information
        'final_final': final_final,
        'final_transmuted': final_transmuted,
        'final_classification': final_classification,

        'final_grade_average': final_grade_average,

    }

    return render(request, 'course.html', context)





def all_announcements_view(request):
    # Fetch all courses for the current user through Enrollment
    user_courses = Course.objects.filter(enrollment__user=request.user)

    # Fetch all announcements related to those courses
    announcements = Announcement.objects.filter(course__in=user_courses)

    # Pass context to the template
    context = {
        'announcements': announcements,
    }

    return render(request, 'all_announcements.html', context)


def all_materials_view(request):
    # Fetch all courses for the current user through Enrollment
    user_courses = Course.objects.filter(enrollment__user=request.user)

    # Fetch all materials related to those courses
    materials = Materials.objects.filter(course__in=user_courses)

    # Create a list of materials with their types
    material_info = []
    for material in materials:
        file_extension = material.content.url.split('.')[-1].lower()  # Get the file extension
        material_info.append({
            'title': material.title,
            'url': material.content.url,
            'type': file_extension,
            'posted_on': material.created_on,
            'course': material.course
        })

    # Pass context to the template
    context = {
        'materials': material_info,  # Use the processed list
    }

    return render(request, 'all_materials.html', context)


def calculate_overall_quiz_grade(user):
    quizzes = Grade.objects.filter(user=user)
    total_score = sum([grade.score for grade in quizzes])
    total_items = sum([grade.quiz.no_of_questions for grade in quizzes])

    if total_items == 0:
        return 0

    return (total_score / total_items) * 60


def calculate_overall_exam_grade(user):
    exams = ExamResult.objects.filter(student=user)
    total_score = sum([exam.score for exam in exams])
    total_items = sum([exam.total_items for exam in exams])

    if total_items == 0:
        return 0

    return (total_score / total_items) * 40

def all_activities_view(request):
    course_pk = request.GET.get('course')  # Check if a specific course is selected
    quiz_pk = request.GET.get('quiz')  # Check if a specific quiz is selected

    if course_pk and quiz_pk:
        # Fetch specific course and quizzes if provided
        course = Course.objects.get(pk=course_pk)
        quizzes = Quiz.objects.filter(course=course)
        results = Grade.objects.filter(quiz__course=course, user=request.user).values('quiz__name', 'score', 'quiz__course_id')
    else:
        # Fetch all courses for the current user through Enrollment
        user_courses = Course.objects.filter(enrollment__user=request.user)

        # Fetch all quizzes related to those courses
        quizzes = Quiz.objects.filter(course__in=user_courses)

        print_mo_to = Quiz.objects.filter(course__in=user_courses).values('time_limit')
        print(print_mo_to)
        # Fetch grades for quizzes related to these courses
        results = Grade.objects.filter(quiz__course__in=user_courses, user=request.user).values('quiz__name', 'score', 'quiz__course_id')

    # Prepare context for rendering
    context = {
        'quizzes': quizzes,
        'results': results,
        'user_courses': user_courses,  # Passing user courses for potential use in the template
    }

    return render(request, 'all_activities.html', context)



def activities_view(request, pk):
    obj = Course.objects.get(pk=pk)
    quizzes = Quiz.objects.filter(course=obj)

    # Filter grades for quizzes related to this course, and get the quiz name and score
    results = Grade.objects.filter(quiz__course=obj, user=request.user).values('quiz__name', 'score')
    results_prof = Grade.objects.filter(quiz__course=obj).values('quiz__name', 'score')
    context = {
        'obj': obj,
        'quizzes': quizzes,
        'results': results,  # Passing both the quiz name and score
    }
    return render(request, 'activities_view.html', context)

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
            return redirect('class:home_view')
        elif user is not None and user.is_admin:
            auth_login(request, user)
            return redirect('class:admin_custom_view')
        else:
            messages.error(request, "Invalid username or password.")  # Add an error message
            return render(request, 'login.html')  # Render the login page again with an error
    else:
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('class:login')


def professor_required(user):
    if not (user.is_professor or user.is_admin):
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


def materials_view(request, pk):
    obj = Course.objects.get(pk=pk)
    materials = Materials.objects.filter(course_id=pk)

    # Create a list of materials with their types
    material_info = []
    for material in materials:
        file_extension = material.content.url.split('.')[-1].lower()  # Get the file extension
        material_info.append({
            'title': material.title,
            'url': material.content.url,
            'type': file_extension,
            'posted_on': material.created_on,
        })

    context = {
        'materials': material_info,
        'obj': obj,  # Your course object or other context data
    }

    return render(request, 'materials_view.html', context)



def add_exam_result_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)  # Get the course by its primary key

    if request.method == 'POST':
        form = ExamResultForm(request.POST)
        if form.is_valid():
            exam_result = form.save(commit=False)
            exam_result.course = course  # Automatically set the course
            exam_result.professor = request.user  # Set the logged-in professor
            exam_result.save()
            return redirect('class:course_view', pk=course.pk)  # Redirect to the course view
    else:
        # Set initial value for the 'course' field in the form
        form = ExamResultForm(initial={'course': course})

    return render(request, 'add_exam_result.html', {'form': form, 'course': course})



@login_required
@user_passes_test(professor_required)
def enroll_student_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if request.method == 'POST':
        # Check if we are trying to enroll or delete
        if 'enroll' in request.POST:
            form = EnrollmentForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']  # Assuming 'user' is a field in your EnrollmentForm
                # Check if the user is already enrolled in this course
                if Enrollment.objects.filter(course=course, user=user).exists():
                    messages.error(request, f"{user.username} is already enrolled in this course.")
                else:
                    enrollment = form.save(commit=False)
                    enrollment.course = course  # Assign the course
                    enrollment.save()  # Save the enrollment
                    return redirect('class:course_view', pk=course.pk)  # Redirect to the course view

        elif 'delete' in request.POST:
            student_id = request.POST.get('student_id')
            enrollment = get_object_or_404(Enrollment, user_id=student_id, course=course)
            enrollment.delete()  # Delete the enrollment
            return redirect('class:course_view', pk=course.pk)  # Redirect to the course view

    else:
        form = EnrollmentForm()

    # Get current enrollments for this course
    current_enrollments = Enrollment.objects.filter(course=course).select_related('user')

    context = {
        'course': course,
        'form': form,
        'enrollments': current_enrollments,
    }
    return render(request, 'enroll_student.html', context)


# View to handle course creation and display all courses
def course_create_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class:course_create_view')  # Redirect back to the same page after saving
    else:
        form = CourseForm()

    # Fetch all courses to display in the template
    courses = Course.objects.all()

    return render(request, 'course_form.html', {'form': form, 'courses': courses})


# View to handle course deletion
def course_delete_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course.delete()
        return redirect('class:admin_custom_view')  # Redirect back to the main page after deletion

    return render(request, 'course_confirm_delete.html', {'course': course})

# View to display enrollments and delete enrollment
def enroll_user_admin(request):
    courses = Course.objects.all()  # Fetch all courses
    enrollments = Enrollment.objects.select_related('course', 'user')  # Fetch all enrollments

    form = EnrollmentFormAdmin()  # Instantiate the form to be visible on page load

    # Handle form submission for adding an enrollment
    if request.method == 'POST' and 'enroll' in request.POST:
        form = EnrollmentFormAdmin(request.POST)
        if form.is_valid():
            form.save()

            return redirect('class:enroll_user_admin')

    # Handle enrollment deletion
    if request.method == 'POST' and 'delete_enrollment' in request.POST:
        enrollment_id = request.POST.get('delete_enrollment')
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.delete()

        return redirect('class:admin_custom_view')

    context = {
        'courses': courses,
        'enrollments': enrollments,
        'form': form,  # Always pass the form to the template
    }
    return render(request, 'enroll_user_admin.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class:admin_custom_view')  # Replace 'login' with your actual login URL

    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def edit_password(request):
    if request.method == 'POST':
        form = AdminPasswordChangeForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('class:admin_custom_view')  # Redirect to avoid form re-submission
    else:
        form = AdminPasswordChangeForm()

    return render(request, 'password_edit.html', {'form': form})

def announcements_view(request, class_id):
    # Order announcements by 'posted_on' in descending order (newest first)
    announcements = Announcement.objects.filter(class_id=class_id).order_by('-posted_on')
    return render(request, 'announcement_view.html', {'announcements': announcements})


def calculate_exam_grade(exams):
    total_score = sum([exam.score for exam in exams])
    total_items = sum([exam.total_items for exam in exams])

    if total_items == 0:
        return 0

    # Formula: [(score1 + score2) / (total1 + total2)] * 40
    return (total_score / total_items) * 40


def calculate_quiz_grade(grades):
    total_score = sum([grade.score for grade in grades])
    total_items = sum([grade.quiz.no_of_questions for grade in grades])

    if total_items == 0:
        return 0

    # Formula: [(score1 + score2) / (total1 + total2)] * 60
    return (total_score / total_items) * 60


def get_grades_by_period(user, period, course):
    # Retrieve quizzes based on the user, period, and course
    quizzes = Grade.objects.filter(user=user, quiz__period=period, quiz__course=course)

    # Retrieve exams based on the user, period, and course (use course directly)
    exams = ExamResult.objects.filter(student=user, period=period, course=course)

    # Calculate the quiz and exam grades
    quiz_grade = calculate_quiz_grade(quizzes)
    exam_grade = calculate_exam_grade(exams)

    # Compute the final grade
    final_grade = quiz_grade + exam_grade

    # Get the transmuted grade and classification based on the final grade
    transmuted_grade, classification = get_transmuted_grade_and_classification(final_grade)
    print(
        f"Computed transmuted grade: {transmuted_grade} and classification: {classification} for final grade: {final_grade}")

    # Iterate through the quizzes to update transmuted_grade and classification fields
    for grade in quizzes:
        grade.transmuted_grade = transmuted_grade  # Assign the transmuted grade
        grade.classification = classification  # Assign the classification
        grade.save()  # Save the changes to the database

    return final_grade, transmuted_grade, classification


def get_prelim_grades(user, course):
    return get_grades_by_period(user, 'prelim', course)

def get_midterm_grades(user, course):
    return get_grades_by_period(user, 'midterm', course)

def get_final_grades(user, course):
    return get_grades_by_period(user, 'final', course)


def grades_view(request, pk):
    # Fetch the course object based on the primary key
    obj = Course.objects.get(pk=pk)

    # Check if the user is a professor
    if request.user.is_professor:
        # Fetch all enrollments related to this course
        enrollments = Enrollment.objects.filter(course=obj)

        # Fetch all students enrolled in the course using the 'user' field from Enrollment
        students = [enrollment.user for enrollment in enrollments]

        # Fetch quiz and exam results for all students
        results_prof = Grade.objects.filter(quiz__course=obj).values('user__username', 'quiz__name', 'score', 'passed', 'period')
        exam_results_prof = ExamResult.objects.filter(course=obj)

        # Calculate grades for each student
        student_grades = []
        for student in students:
            prelim_final, prelim_transmuted, prelim_classification = get_prelim_grades(student, obj)
            midterm_final, midterm_transmuted, midterm_classification = get_midterm_grades(student, obj)
            final_final, final_transmuted, final_classification = get_final_grades(student, obj)

            total_final_grades = prelim_final + midterm_final + final_final
            final_grade_average = total_final_grades / 3

            student_grades.append({
                'student': student,
                'prelim_final': prelim_final,
                'midterm_final': midterm_final,
                'final_final': final_final,
                'final_grade_average': final_grade_average
            })

        context = {
            'obj': obj,
            'students': students,
            'student_grades': student_grades,
            'exam_results_prof': exam_results_prof,  # Exam results for professor's view
            'results_prof': results_prof,  # Quiz results for professor's view
        }

    else:
        # Fetch grades for the logged-in student
        exam_results = ExamResult.objects.filter(course=obj, student=request.user)
        results = Grade.objects.filter(quiz__course=obj, user=request.user).values('quiz__name', 'score', 'period')

        # Calculate logged-in student's grades
        prelim_final, prelim_transmuted, prelim_classification = get_prelim_grades(user=request.user, course=obj)
        midterm_final, midterm_transmuted, midterm_classification = get_midterm_grades(user=request.user, course=obj)
        final_final, final_transmuted, final_classification = get_final_grades(user=request.user, course=obj)

        total_final_grades = prelim_final + midterm_final + final_final
        final_grade_average = total_final_grades / 3

        context = {
            'obj': obj,
            'results': results,
            'exam_results': exam_results,
            'prelim_final': prelim_final,
            'midterm_final': midterm_final,
            'final_final': final_final,
            'final_grade_average': final_grade_average,
        }

    return render(request, 'grades_view.html', context)



def get_transmuted_grade_and_classification(final_grade):
    """
    Maps a computed average to the corresponding transmuted grade and general classification.
    """
    if 95.2 <= final_grade <= 100.0000:
        return 1.00, "Outstanding"
    elif 90.4 <= final_grade < 95.1999:
        return 1.25, "Excellent"
    elif 85.6 <= final_grade < 90.3999:
        return 1.50, "Superior"
    elif 80.8 <= final_grade < 85.5999:
        return 1.75, "Very Good"
    elif 76.0000 <= final_grade < 80.7999:
        return 2.00, "Good"
    elif 71.2 <= final_grade < 75.9999:
        return 2.25, "Satisfactory"
    elif 66.4 <= final_grade < 71.1999:
        return 2.50, "Fairly Satisfactory"
    elif 61.6 <= final_grade < 66.3999:
        return 2.75, "Fair"
    elif 60 <= final_grade < 61.5999:
        return 3.00, "Passed"
    else:
        return 5.00, "Failed"  # Assign 5.00 for failed grades below 75



