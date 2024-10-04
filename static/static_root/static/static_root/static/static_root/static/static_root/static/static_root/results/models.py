from django.db import models
from quizzes.models import Quiz
from django.conf import settings

class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField

    def __str__(self):
        return str(self.pk)
# Create your models here.
