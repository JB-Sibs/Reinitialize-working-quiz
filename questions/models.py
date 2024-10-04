from django.db import models
from quizzes.models import Quiz

class Question(models.Model):
    text = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.text)

    def get_answers(self):
        """Return all answers related to this question."""
        return self.answer_set.all()

    def get_correct_answer(self):
        """Return the correct answer for this question."""
        correct_answer = self.answer_set.filter(correct=True).first()
        return correct_answer if correct_answer else None


class Answer(models.Model):
    text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Question: {self.question.text}, Answer: {self.text}, Correct: {self.correct}"
