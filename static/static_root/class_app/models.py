from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.core.exceptions import PermissionDenied

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='assignments/')
    description = models.TextField()
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_on = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/')

    def __str__(self):
        return f"{self.student} submitted {self.assignment}"

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class User(AbstractUser):

    is_professor = models.BooleanField('is professor', default=False)
    is_student = models.BooleanField('is student', default=False)

    # def has_perms(self, perm_list):
    #     return True

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    enrolled_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} enrolled in {self.course}"

class Grade(models.Model):
    grade_value = models.CharField(max_length=3)
    grade_type = models.CharField(max_length=50)
    date_recorded = models.DateField(auto_now_add=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    Course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    assignment_id = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.grade_value} - {self.student_id} - {self.Course_id}"

class Materials(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.FileField(upload_to='modules/pdfs/')  # PDF file upload
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by.is_professor:
            raise PermissionDenied("Only professors can create modules.")
        super().save(*args, **kwargs)
# Create your models here.
