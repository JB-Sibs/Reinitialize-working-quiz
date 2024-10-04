from django.db import models
from class_app.models import Course
class Quiz(models.Model):
    name = models.CharField(max_length=120)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic = models.CharField(max_length=120)
    no_of_questions = models.IntegerField()
    time = models.IntegerField(help_text="duration of the quiz")
    req_score_to_pass = models.IntegerField(help_text="score to pass")

    def __str__(self):
        return f"{self.name}-{self.topic}"

    def get_questions(self):
        return self.questions_set.all()

    class Meta:
        verbose_name_plural = 'Quizzes'
# Create your models here.
