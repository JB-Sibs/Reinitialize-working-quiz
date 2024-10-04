from django.contrib import admin
from .models import Course, Enrollment, Assignment, Submission, User, Grade, Announcement, Materials
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    # Modify the fieldsets, instead of appending duplicate fields
    fieldsets = list(BaseUserAdmin.fieldsets)

    # Modify the fieldset that contains 'email', which is usually under 'Personal info'
    fieldsets[1] = (None, {'fields': ('email', 'first_name', 'last_name')})

    # Adding custom fields for 'is_professor' and 'is_student'
    fieldsets.append((None, {'fields': ('is_professor', 'is_student')}))

    # Customize the list display
    list_display = BaseUserAdmin.list_display + ('is_professor', 'is_student')

    # Add custom fields to the user creation form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'is_professor', 'is_student')}),
    )


# Register the models with the custom UserAdmin
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(User, UserAdmin)
admin.site.register(Grade)
admin.site.register(Announcement)
admin.site.register(Materials)
