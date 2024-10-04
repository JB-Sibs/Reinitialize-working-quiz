from django.contrib import admin
from .models import Course, Enrollment, Assignment, Submission, User, Grade, Announcement, Materials
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    # Specify the fields to be displayed in the admin panel
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_professor', 'is_student')}),
    )

    # Specify the fields to be included in the add form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_professor', 'is_student')}),
    )

    # Optionally, you can customize the list display
    list_display = BaseUserAdmin.list_display + ('is_professor', 'is_student')


# Register the models with the custom UserAdmin
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(User, UserAdmin)
admin.site.register(Grade)
admin.site.register(Announcement)
admin.site.register(Materials)