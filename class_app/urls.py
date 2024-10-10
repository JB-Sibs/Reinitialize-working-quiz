

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
    path('course/<int:course_pk>/exam/add/',add_exam_result_view, name='add_exam_result'),
    # Additional URL patterns for other views if needed
]
