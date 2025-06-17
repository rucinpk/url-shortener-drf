"""
URL configuration for the shortener app.
Following RESTful API design principles.
"""
from django.urls import path
from .views import (
    CreateShortenedURLView,
    URLStatsView,
    HealthCheckView
)

app_name = 'shortener'

urlpatterns = [
    # API endpoints
    path('shorten/', CreateShortenedURLView.as_view(), name='create_shortened_url'),
    path('stats/<str:short_code>/', URLStatsView.as_view(), name='url_stats'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
] 