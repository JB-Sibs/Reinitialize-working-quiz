from django.urls import path
from .views import *

app_name = 'quizzes'

urlpatterns = [
    # Existing quiz-related URLs

    path('course/<int:course_pk>/<int:quiz_pk>/', quiz_view, name='quiz_view'),
    path('course/<int:course_pk>/<int:quiz_pk>/save/', save_quiz_view, name='save_view'),
    path('course/<int:course_pk>/<int:quiz_pk>/data/', quiz_data_view, name='quiz_data_view'),

    # URL to create a quiz (for professors)
    path('course/<int:course_pk>/create_quiz/', create_quiz_view, name='create_quiz'),

    # URL to add questions to a quiz
    path('quiz/<int:quiz_id>/add_question/', add_question_view, name='add_question'),
    # New URL to handle the prepared quiz and redirect to the course page
    path('quiz/<int:quiz_id>/prepared/<int:course_pk>/', quiz_prepared_view, name='quiz_prepared'),
    path('quiz/<slug:slug>/grades/', quiz_grades, name='quiz-grades'),
]
