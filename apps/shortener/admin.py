"""
Django admin configuration for URL shortener models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ShortenedURL, URLClick


@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    """
    Admin interface for ShortenedURL model.
    """
    
    list_display = [
        'short_code',
        'original_url_display',
        'title',
        'click_count',
        'is_active',
        'is_expired',
        'created_at',
        'expires_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'expires_at',
    ]
    
    search_fields = [
        'short_code',
        'original_url',
        'title',
        'description'
    ]
    
    readonly_fields = [
        'short_code',
        'click_count',
        'created_at',
        'updated_at',
        'last_accessed_at',
        'is_expired'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('URL Information', {
            'fields': ('original_url', 'short_code', 'title', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at', 'is_expired')
        }),
        ('Statistics', {
            'fields': ('click_count', 'last_accessed_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by_ip'),
            'classes': ('collapse',)
        }),
    )
    
    def original_url_display(self, obj):
        """Display truncated original URL with link."""
        if len(obj.original_url) > 50:
            display_url = obj.original_url[:47] + '...'
        else:
            display_url = obj.original_url
        
        return format_html(
            '<a href="{}" target="_blank" title="{}">{}</a>',
            obj.original_url,
            obj.original_url,
            display_url
        )
    original_url_display.short_description = 'Original URL'
    
    def is_expired(self, obj):
        """Display expiration status."""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(URLClick)
class URLClickAdmin(admin.ModelAdmin):
    """
    Admin interface for URLClick model.
    """
    
    list_display = [
        'shortened_url_display',
        'clicked_at',
        'ip_address',
        'user_agent_display'
    ]
    
    list_filter = [
        'clicked_at',
        'shortened_url__short_code'
    ]
    
    search_fields = [
        'shortened_url__short_code',
        'ip_address',
        'user_agent'
    ]
    
    readonly_fields = [
        'shortened_url',
        'clicked_at',
        'ip_address',
        'user_agent',
        'referer'
    ]
    
    ordering = ['-clicked_at']
    
    def shortened_url_display(self, obj):
        """Display short code with link to URL stats."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:shortener_shortenedurl_change', args=[obj.shortened_url.pk]),
            obj.shortened_url.short_code
        )
    shortened_url_display.short_description = 'Short Code'
    
    def user_agent_display(self, obj):
        """Display truncated user agent."""
        if not obj.user_agent:
            return '-'
        
        if len(obj.user_agent) > 50:
            return obj.user_agent[:47] + '...'
        return obj.user_agent
    user_agent_display.short_description = 'User Agent'
    
    def has_add_permission(self, request):
        """Disable adding clicks through admin."""
        return False 