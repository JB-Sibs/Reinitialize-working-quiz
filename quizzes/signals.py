# quizzes/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Quiz
from class_app.models import Course  # Import Course here to avoid circular import in models

@receiver(post_save, sender=Quiz)
def update_course_on_quiz_save(sender, instance, **kwargs):
    course = instance.course
    # Example: Perform any action related to Course when Quiz is saved
    course.last_quiz_updated = instance.name  # Hypothetical field
    course.save()
