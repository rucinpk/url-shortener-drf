"""
Domain models for URL shortening functionality.
Following clean architecture principles with clear separation of concerns.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class ShortenedURL(models.Model):
    """
    Core entity representing a shortened URL.
    
    This model represents the main business entity in our domain.
    It contains the essential data and business rules for URL shortening.
    """
    
    original_url = models.URLField(
        max_length=2048,
        help_text="The original long URL to be shortened"
    )
    
    short_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="The unique short code used in the shortened URL"
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional title for the URL"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description for the URL"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the URL was shortened"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the URL was last updated"
    )
    
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional expiration date for the shortened URL"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the shortened URL is active"
    )
    
    # Tracking fields
    click_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this shortened URL has been accessed"
    )
    
    last_accessed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the URL was last accessed"
    )
    
    created_by_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address that created this shortened URL"
    )

    class Meta:
        db_table = 'shortened_urls'
        verbose_name = 'Shortened URL'
        verbose_name_plural = 'Shortened URLs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}"

    def clean(self):
        """
        Custom validation for the model.
        Business rules validation should be here.
        """
        super().clean()
        
        # Validate URL format
        validator = URLValidator()
        try:
            validator(self.original_url)
        except ValidationError:
            raise ValidationError({
                'original_url': 'Please enter a valid URL.'
            })
        
        # Check if URL is not expired
        if self.expires_at and self.expires_at < timezone.now():
            raise ValidationError({
                'expires_at': 'Expiration date cannot be in the past.'
            })

    def save(self, *args, **kwargs):
        """Override save to ensure clean validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if the shortened URL has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_available(self):
        """Check if the shortened URL is available for use"""
        return self.is_active and not self.is_expired

    def increment_click_count(self):
        """
        Business logic method to increment click count.
        This encapsulates the business rule for tracking clicks.
        """
        self.click_count += 1
        self.last_accessed_at = timezone.now()
        self.save(update_fields=['click_count', 'last_accessed_at'])


class URLClick(models.Model):
    """
    Entity for tracking individual URL clicks.
    
    This allows for detailed analytics and tracking of URL usage.
    Separated from ShortenedURL to follow single responsibility principle.
    """
    
    shortened_url = models.ForeignKey(
        ShortenedURL,
        on_delete=models.CASCADE,
        related_name='clicks',
        help_text="The shortened URL that was clicked"
    )
    
    clicked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the URL was clicked"
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the user who clicked the URL"
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User agent string of the browser"
    )
    
    referer = models.URLField(
        blank=True,
        null=True,
        help_text="The referring URL"
    )

    class Meta:
        db_table = 'url_clicks'
        verbose_name = 'URL Click'
        verbose_name_plural = 'URL Clicks'
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['shortened_url', 'clicked_at']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"Click on {self.shortened_url.short_code} at {self.clicked_at}" 