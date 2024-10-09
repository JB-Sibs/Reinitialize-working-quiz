from django.urls import path
from .views import quiz_grades  # Import the view properly

app_name = 'results'

urlpatterns = [
    # Do not call the function, just pass it as a reference
    path('<str:pk>/', quiz_grades, name='quiz_grades'),
]
