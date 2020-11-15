from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name="welcome"),
    #path('profile/<str:user>/', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),
    path('logs/', views.logs, name='logs'),
    path('logs/new/', views.logs_new, name='logs_new'),
    path('logs/<int:pk>/edit/', views.logs_edit, name='logs_edit'),
    path('projects/', views.projects, name='projects'),
    path('projects/<str:slug>/', views.project_view, name='project_view'),
    path('projects/<str:slug>/edit', views.project_edit, name='project_edit'),
    path('projects/new/', views.project_new, name='project_new'),
    path('stats/<str:mode>/', views.stats, name='stats'),
    path('stats/', views.stats, name='stats'),
    # path('upload/csv/', views.upload_csv, name='upload_csv'),
]