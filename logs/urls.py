from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name="welcome"),
    #path('profile/<str:user>/', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),
    path('logs/', views.logs, name='logs'),
    path('projects/', views.projects, name='projects'),
    path('projects/<str:slug>/', views.project_detail, name='project_detail'),
    path('stats/<str:mode>/', views.stats, name='stats'),
    path('stats/', views.stats, name='stats'),
    # path('upload/csv/', views.upload_csv, name='upload_csv'),
]