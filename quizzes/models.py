from django.db import models

import random



class Quiz(models.Model):
    PERIOD_CHOICES = [
        ('prelim', 'Prelim'),
        ('midterm', 'Midterm'),
        ('final', 'Final'),
    ]
    name = models.CharField(max_length=120)
    course = models.ForeignKey('class_app.Course', on_delete=models.CASCADE)
    topic = models.CharField(max_length=120)
    no_of_questions = models.IntegerField()
    time = models.IntegerField(help_text="Duration of the quiz in minutes")
    req_score_to_pass = models.FloatField(help_text="Score to pass")
    period = models.CharField(max_length=7, choices=PERIOD_CHOICES, default='prelim')
    attempts_allowed = models.IntegerField(default=1, help_text="Number of attempts allowed")
    time_limit = models.IntegerField(default=30, help_text="Time limit for each attempt in minutes")

    # New field to choose period
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
