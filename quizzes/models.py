from django.db import models

import random
from django.utils.text import slugify
class Quiz(models.Model):
    name = models.CharField(max_length=120)
    course = models.ForeignKey('class_app.Course', on_delete=models.CASCADE)  # String reference to avoid direct import
    topic = models.CharField(max_length=120)
    no_of_questions = models.IntegerField()
    time = models.IntegerField(help_text="duration of the quiz")
    req_score_to_pass = models.FloatField(help_text="score to pass")

    def __str__(self):
        return f"{self.name} - {self.topic}"

    def __str__(self):
        return f"{self.name}-{self.topic}"

    def get_questions(self):
        questions = list(self.question_set.all())
        random.shuffle(questions)
        return questions[:self.no_of_questions]

    class Meta:
        verbose_name_plural = 'Quizzes'
# Create your models here.
