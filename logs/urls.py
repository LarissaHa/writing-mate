from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name="welcome"),
    #path('profile/<str:user>/', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),
    path('logs/', views.logs, name='logs'),
    path('logs/new/', views.logs_new, name='logs_new'),
    path('logs/filter/<str:slug>/', views.logs, name='logs_filter'),
    path('logs/<int:pk>/edit/', views.logs_edit, name='logs_edit'),
    path('logs/<int:pk>/delete/', views.logs_delete, name='logs_delete'),
    path('projects/', views.projects, name='projects'),
    path('projects/new/', views.project_new, name='project_new'),
    path('projects/<str:slug>/', views.project_view, name='project_view'),
    path('projects/<str:slug>/edit', views.project_edit, name='project_edit'),
    path('projects/<str:slug>/delete', views.project_delete, name='project_delete'),
    path('stats/<str:mode>/', views.stats, name='stats'),
    path('stats/', views.stats, name='stats'),
    path('imprint/', views.imprint, name='imprint'),
    path('contact/', views.contact, name='contact'),
    path('release_notes/', views.release_notes, name='release_notes'),
    path('accounts/register/', views.register, name='register'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('not_allowed/', views.not_allowed, name='not_allowed'),
    # path('upload/csv/', views.upload_csv, name='upload_csv'),
]