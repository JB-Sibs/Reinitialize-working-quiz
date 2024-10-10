from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
                  path('admin/', admin.site.urls),  # Ensure this is only declared once.

                  path('password_reset/',
                       auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),
                       name='password_reset'),
                  path('password_reset/done/',
                       auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
                       name='password_reset_done'),
                  path('reset/<uidb64>/<token>/',
                       auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
                       name='password_reset_confirm'),
                  path('reset/done/',
                       auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
                       name='password_reset_complete'),

                  path('', include('class_app.urls')),  # Class app routes
                  path('', include('quizzes.urls', namespace='quizzes')),  # Quizzes app routes


              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
