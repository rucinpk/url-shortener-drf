"""
Service layer for URL shortening business logic.
Following clean architecture principles with clear separation of concerns.

This layer contains the application's business logic and use cases.
It orchestrates the interaction between the domain models and external services.
"""
import uuid
import hashlib
import time
import validators
from typing import Optional, Dict, Any
from hashids import Hashids
from django.conf import settings
from django.utils import timezone
from django.db import transaction


from .models import ShortenedURL, URLClick
from .exceptions import URLShortenerError, URLNotFoundError, URLExpiredError


class URLShortenerService:
    """
    Service class encapsulating URL shortening business logic.
    
    This service handles the core use cases:
    - Creating shortened URLs
    - Retrieving original URLs
    - Tracking URL usage
    """
    
    def __init__(self):
        """Initialize the service with configuration from settings."""
        config = settings.URL_SHORTENER
        self.domain = config['DOMAIN']
        self.hashids = Hashids(
            salt=config['HASHIDS_SALT'],
            min_length=config['HASHIDS_MIN_LENGTH']
        )
    
    def shorten_url(
        self, 
        original_url: str, 
        title: Optional[str] = None,
        description: Optional[str] = None,
        expires_at: Optional[timezone.datetime] = None,
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a shortened URL from an original URL.
        
        Args:
            original_url: The URL to be shortened
            title: Optional title for the URL
            description: Optional description
            expires_at: Optional expiration datetime
            client_ip: IP address of the client creating the URL
            
        Returns:
            Dictionary containing shortened URL information
            
        Raises:
            URLShortenerError: If URL validation fails or creation fails
        """
        # Validate the URL format
        if not validators.url(original_url):
            raise URLShortenerError("Invalid URL format provided")
        
        # Check if URL already exists
        existing_url = self._find_existing_url(original_url)
        if existing_url and existing_url.is_available:
            return self._format_url_response(existing_url)
        
        try:
            with transaction.atomic():                
                short_code = self._generate_short_code(original_url)
                shortened_url = ShortenedURL(
                    original_url=original_url,
                    title=title,
                    description=description,
                    expires_at=expires_at,
                    created_by_ip=client_ip,
                    short_code=short_code
                )
                shortened_url.save()
                
                return self._format_url_response(shortened_url)
                
        except Exception as e:
            raise URLShortenerError(f"Failed to create shortened URL: {str(e)}")
    
    def get_original_url(self, short_code: str, track_click: bool = True) -> Dict[str, Any]:
        """
        Retrieve the original URL from a short code.
        
        Args:
            short_code: The short code to resolve
            track_click: Whether to track this as a click
            
        Returns:
            Dictionary containing original URL and metadata
            
        Raises:
            URLNotFoundError: If short code doesn't exist
            URLExpiredError: If URL has expired
        """
        try:
            shortened_url = ShortenedURL.objects.get(short_code=short_code)
        except ShortenedURL.DoesNotExist:
            raise URLNotFoundError(f"Short code '{short_code}' not found")
        
        # Check if URL is available
        if not shortened_url.is_active:
            raise URLNotFoundError(f"Short code '{short_code}' is not active")
        
        if shortened_url.is_expired:
            raise URLExpiredError(f"Short code '{short_code}' has expired")
        
        # Track the click if requested
        if track_click:
            shortened_url.increment_click_count()
        
        return {
            'original_url': shortened_url.original_url,
            'short_code': shortened_url.short_code,
            'title': shortened_url.title,
            'description': shortened_url.description,
            'click_count': shortened_url.click_count,
            'created_at': shortened_url.created_at,
            'expires_at': shortened_url.expires_at,
        }
    
    def get_url_stats(self, short_code: str) -> Dict[str, Any]:
        """
        Get statistics for a shortened URL.
        
        Args:
            short_code: The short code to get stats for
            
        Returns:
            Dictionary containing URL statistics
            
        Raises:
            URLNotFoundError: If short code doesn't exist
        """
        try:
            shortened_url = ShortenedURL.objects.get(short_code=short_code)
        except ShortenedURL.DoesNotExist:
            raise URLNotFoundError(f"Short code '{short_code}' not found")
        
        return {
            'short_code': shortened_url.short_code,
            'original_url': shortened_url.original_url,
            'title': shortened_url.title,
            'description': shortened_url.description,
            'click_count': shortened_url.click_count,
            'created_at': shortened_url.created_at,
            'last_accessed_at': shortened_url.last_accessed_at,
            'expires_at': shortened_url.expires_at,
            'is_active': shortened_url.is_active,
            'is_expired': shortened_url.is_expired,
        }
    
    def track_click(
        self, 
        short_code: str, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None
    ) -> None:
        """
        Track a click on a shortened URL.
        
        Args:
            short_code: The short code that was clicked
            ip_address: IP address of the clicker
            user_agent: User agent string
            referer: Referring URL
        """
        try:
            shortened_url = ShortenedURL.objects.get(short_code=short_code)
            
            URLClick.objects.create(
                shortened_url=shortened_url,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer
            )
            
        except ShortenedURL.DoesNotExist:
            # Don't raise error for click tracking to avoid breaking redirects
            pass
    
    def _find_existing_url(self, original_url: str) -> Optional[ShortenedURL]:
        """
        Find an existing shortened URL for the given original URL.
        
        Args:
            original_url: The original URL to search for
            
        Returns:
            ShortenedURL instance if found, None otherwise
        """
        try:
            return ShortenedURL.objects.filter(
                original_url=original_url,
                is_active=True
            ).first()
        except Exception:
            return None
    
    def _generate_short_code(self, url: str) -> str:
        """
        Generate a short code from the URL using Hashids.
        
        Args:
            url: The original URL to generate a short code for
            
        Returns:
            Generated short code
        """
        hash_input = f"{url}"
        url_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        hash_int = int(url_hash[:16], 16)
        
        return self.hashids.encode(hash_int)
    
    def _format_url_response(self, shortened_url: ShortenedURL) -> Dict[str, Any]:
        """
        Format a ShortenedURL instance into a response dictionary.
        
        Args:
            shortened_url: The ShortenedURL instance
            
        Returns:
            Formatted response dictionary
        """
        return {
            'short_code': shortened_url.short_code,
            'short_url': f"{self.domain.rstrip('/')}/shrt/{shortened_url.short_code}",
            'original_url': shortened_url.original_url,
            'title': shortened_url.title,
            'description': shortened_url.description,
            'created_at': shortened_url.created_at,
            'expires_at': shortened_url.expires_at,
            'click_count': shortened_url.click_count,
        } 