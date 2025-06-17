"""
Custom exceptions for URL shortener application.
Following clean architecture principles with domain-specific exceptions.
"""


class URLShortenerError(Exception):
    """Base exception for URL shortener related errors."""
    pass


class URLNotFoundError(URLShortenerError):
    """Raised when a short code is not found."""
    pass


class URLExpiredError(URLShortenerError):
    """Raised when a shortened URL has expired."""
    pass


class InvalidURLError(URLShortenerError):
    """Raised when an invalid URL is provided."""
    pass 