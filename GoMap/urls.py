from django.urls import path
from . import views
from django.contrib import admin
from django.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.goals, name="gomap_home"),
    path('test/', views.test_view, name='test_view'),
    path('subgoal/<int:pk>/', views.subgoal_detail, name='subgoal_detail'),
    path('step/<int:step_id>/toggle/', views.toggle_step_completion, name='toggle_step'),

] 
