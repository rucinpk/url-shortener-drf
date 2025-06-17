"""
URL Configuration for url_shortener project
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.shortener.views import RedirectURLView


schema_view = get_schema_view(
    openapi.Info(
        title="URL Shortener API",
        default_version='v1',
        description="A clean and efficient URL shortening service API",
        contact=openapi.Contact(email="contact@urlshortener.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('shrt/<str:short_code>/', RedirectURLView.as_view(), name='redirect_url'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.shortener.urls')),
    
    # Swagger documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
] 