
from django.urls import path
from .import views
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),  
    path('edit/', views.edit, name='edit'),
    path('delete/', views.delete, name='delete'), 
    path('register/', views.reg, name='register'),
    path('reminder/', views.add_reminder, name='reminder'),
    path('rempages/', views.rempages, name='rempages'),
    path('db-status/', views.db_status, name='db_status'),
    path('api/upcoming/', views.upcoming_reminders, name='api_upcoming_reminders'),
    path('api/all/', views.all_user_reminders, name='api_all_reminders'),
    path('api/mark-notified/<int:id>/', views.mark_reminder_notified, name='api_mark_notified'),
    path('add-reminder/', views.add_reminder, name='add_reminder'),

    path('view/', views.viewReminders, name='viewReminders'),
    path('edit/<int:id>/', views.editReminder, name='editReminder'),
    path('delete/<int:id>/', views.deleteReminder, name='deleteReminder'),
    path("get_due_reminders/", views.get_due_reminders, name="get_due_reminders"),
]

