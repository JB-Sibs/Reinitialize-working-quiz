from django.db.models.signals import post_save
from django.dispatch import receiver
from results.models import Result
from class_app.models import Grade
from quizzes.models import Quiz

@receiver(post_save, sender=Result)
def update_grade(sender, instance, created, **kwargs):
    if created:
        # Fetch the student's quiz and calculate whether they passed or failed
        quiz = instance.quiz
        score = instance.score  # Assuming 'score' is a FloatField in Result

        # Check if the student passed
        passed = score >= quiz.req_score_to_pass

        # Create or update the Grade object for this student
        grade, created = Grade.objects.update_or_create(
            user=instance.user,
            quiz=quiz,
            defaults={
                'score': score,
                'passed': passed
            }
        )