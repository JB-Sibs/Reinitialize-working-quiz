

from django.urls import path
from .views import *
app_name = 'class'
urlpatterns = [
    path('homepage/', home_view, name='home_view'),
    path('', login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('professor/', professor_dashboard, name='professor_dashboard'),
    path('change-password/', change_password, name='change_password'),
    path('course/<int:pk>/', course_view, name='course_view'),
    path('course/<int:pk>/add_announcement', add_announcement, name='add_announcement'),
    path('course/<int:pk>/add_module', add_module, name='add_module'),
    path('course/<int:pk>/announcements', announcement_view, name='announcement_view'),
    path('course/<int:pk>/materials', materials_view, name='materials_view'),
    path('course/<int:pk>/activities', activities_view, name='activities_view'),
    path('course/<int:pk>/grades', grades_view, name='grades_view'),
    path('course/<int:course_pk>/exam/add/', add_exam_result_view, name='add_exam_result'),
    path('announcements/', all_announcements_view, name='all_announcements_view'),
    path('materials/', all_materials_view, name='all_materials_view'),
    path('course/<int:course_pk>/enroll/', enroll_student_view, name='enroll_student'),
    path('custom-admin/dashboard/',admin_custom_view, name='admin_custom_view'),
    path('course/new/',course_create_view, name='course_create_view'),
    path('course/<int:pk>/delete/', course_delete_view, name='course_delete_view'),
    path('custom-admin/dashboard/enroll/',enroll_user_admin, name='enroll_user_admin'),
    path('register/', register, name='register'),
    path('edit-password/', edit_password, name='edit_password'),
    path('activities/', all_activities_view, name='all_activities_view'),
    # Additional URL patterns for other views if needed
]
