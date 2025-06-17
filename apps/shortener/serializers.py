"""
Serializers for URL shortener API.
Following clean architecture principles with clear data validation and transformation.
"""
from rest_framework import serializers
from django.utils import timezone
import validators
from .models import ShortenedURL

class CreateShortenedURLSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a shortened URL.
    
    This serializer handles input validation for URL shortening requests.
    """
    
    original_url = serializers.URLField(
        max_length=2048,
        help_text="The original long URL to be shortened",
        error_messages={
            'invalid': 'Please enter a valid URL (including http:// or https://)',
            'max_length': 'URL is too long. Maximum length is 2048 characters.',
        }
    )
    
    title = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Optional title for the shortened URL"
    )
    
    description = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="Optional description for the shortened URL"
    )
    
    expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Optional expiration date and time (ISO 8601 format)"
    )
    
    def validate_original_url(self, value):
        """
        Validate the original URL format and accessibility.
        """
        if not validators.url(value):
            raise serializers.ValidationError(
                "Please provide a valid URL including protocol (http:// or https://)"
            )
        
        # Additional URL format validation
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "URL must start with http:// or https://"
            )
        
        return value
    
    def validate_expires_at(self, value):
        """
        Validate expiration date is in the future.
        """
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiration date must be in the future"
            )
        return value
    
    class Meta:
        model = ShortenedURL
        fields = ['original_url', 'title', 'description', 'expires_at']


class ShortenedURLResponseSerializer(serializers.Serializer):
    """
    Serializer for shortened URL response data.
    
    This serializer formats the response data for successfully created shortened URLs.
    """
    
    short_code = serializers.CharField(
        help_text="The unique short code for the URL"
    )
    
    short_url = serializers.URLField(
        help_text="The complete shortened URL"
    )
    
    original_url = serializers.URLField(
        help_text="The original long URL"
    )
    
    title = serializers.CharField(
        allow_null=True,
        help_text="Title of the shortened URL"
    )
    
    description = serializers.CharField(
        allow_null=True,
        help_text="Description of the shortened URL"
    )
    
    created_at = serializers.DateTimeField(
        help_text="When the URL was created"
    )
    
    expires_at = serializers.DateTimeField(
        allow_null=True,
        help_text="When the URL expires (if set)"
    )
    
    click_count = serializers.IntegerField(
        help_text="Number of times the URL has been accessed"
    )


class URLStatsSerializer(serializers.Serializer):
    """
    Serializer for URL statistics data.
    """
    
    short_code = serializers.CharField(
        help_text="The unique short code for the URL"
    )
    
    original_url = serializers.URLField(
        help_text="The original long URL"
    )
    
    title = serializers.CharField(
        allow_null=True,
        help_text="Title of the shortened URL"
    )
    
    description = serializers.CharField(
        allow_null=True,
        help_text="Description of the shortened URL"
    )
    
    click_count = serializers.IntegerField(
        help_text="Number of times the URL has been accessed"
    )
    
    created_at = serializers.DateTimeField(
        help_text="When the URL was created"
    )
    
    last_accessed_at = serializers.DateTimeField(
        allow_null=True,
        help_text="When the URL was last accessed"
    )
    
    expires_at = serializers.DateTimeField(
        allow_null=True,
        help_text="When the URL expires (if set)"
    )
    
    is_active = serializers.BooleanField(
        help_text="Whether the URL is active"
    )
    
    is_expired = serializers.BooleanField(
        help_text="Whether the URL has expired"
    )


class RedirectResponseSerializer(serializers.Serializer):
    """
    Serializer for redirect response data.
    """
    
    original_url = serializers.URLField(
        help_text="The original URL to redirect to"
    )
    
    short_code = serializers.CharField(
        help_text="The short code that was accessed"
    )
    
    title = serializers.CharField(
        allow_null=True,
        help_text="Title of the shortened URL"
    )
    
    description = serializers.CharField(
        allow_null=True,
        help_text="Description of the shortened URL"
    )


class ErrorSerializer(serializers.Serializer):
    """
    Serializer for error responses.
    """
    
    error = serializers.CharField(
        help_text="Error message"
    )
    
    code = serializers.CharField(
        help_text="Error code",
        required=False
    )
    
    details = serializers.DictField(
        help_text="Additional error details",
        required=False
    ) 