from django.urls import path
from django.views.generic import TemplateView
from .views import register

urlpatterns = [
    path('', TemplateView.as_view(template_name='roadmap/home.html'), name='roadmap_home'),
    path('register/', register, name='register'),
]