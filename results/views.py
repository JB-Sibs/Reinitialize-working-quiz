from django.shortcuts import render, get_object_or_404
from class_app.models import Grade
from quizzes.models import Quiz


def quiz_grades(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    grades = Grade.objects.filter(quiz=quiz)

    context = {
        'quiz': quiz,
        'grades': grades,
    }

    return render(request, 'course.html', context)

# Create your views here.
