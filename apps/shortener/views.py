"""
Class-based views for URL shortener API.
Following clean architecture with clear separation of concerns between
presentation layer (views) and business logic (services).
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services import URLShortenerService
from .serializers import (
    CreateShortenedURLSerializer,
    ShortenedURLResponseSerializer,
    URLStatsSerializer,
    RedirectResponseSerializer,
    ErrorSerializer
)
from .exceptions import URLShortenerError, URLNotFoundError, URLExpiredError


class CreateShortenedURLView(APIView):
    """
    API view for creating shortened URLs.
    
    This view handles POST requests to create new shortened URLs.
    It follows clean architecture by delegating business logic to the service layer.
    """
    
    @swagger_auto_schema(
        operation_description="Create a shortened URL from an original URL",
        operation_summary="Create Shortened URL",
        operation_id="create_shortened_url",
        tags=["URL Shortening"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['original_url'],
            properties={
                'original_url': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_URI,
                    description='The original URL to be shortened',
                    example='https://www.example.com/very/long/path/to/resource?param=value'
                ),
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Optional title for the shortened URL',
                    example='Example Website'
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Optional description for the shortened URL',
                    example='A sample website for demonstration purposes'
                ),
                'expires_at': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description='Optional expiration date and time (ISO 8601 format)',
                    example='2026-12-31T23:59:59Z'
                )
            },
            examples={
                'basic_example': {
                    'summary': 'Basic URL shortening',
                    'description': 'Simple example with just the required URL',
                    'value': {
                        'original_url': 'https://www.google.com'
                    }
                },
                'complete_example': {
                    'summary': 'Complete URL shortening',
                    'description': 'Example with all optional fields included',
                    'value': {
                        'original_url': 'https://docs.djangoproject.com/en/stable/',
                        'title': 'Django Documentation',
                        'description': 'Official Django framework documentation',
                        'expires_at': '2026-12-31T23:59:59Z'
                    }
                },
                'social_media_example': {
                    'summary': 'Social media link',
                    'description': 'Example for social media profile link',
                    'value': {
                        'original_url': 'https://twitter.com/username/status/1234567890',
                        'title': 'Twitter Post',
                        'description': 'Link to an important tweet'
                    }
                },
                'temporary_link_example': {
                    'summary': 'Temporary link',
                    'description': 'Example of a link that expires in a few days',
                    'value': {
                        'original_url': 'https://example.com/temporary-offer',
                        'title': 'Limited Time Offer',
                        'description': 'Special promotion valid until end of month',
                        'expires_at': '2026-01-31T23:59:59Z'
                    }
                }
            }
        ),
        responses={
            201: openapi.Response(
                description="Shortened URL created successfully",
                schema=ShortenedURLResponseSerializer
            ),
            400: openapi.Response(
                description="Bad request - Invalid input data",
                schema=ErrorSerializer
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=ErrorSerializer
            )
        }
    )
    def post(self, request):
        """
        Create a new shortened URL.
        
        Args:
            request: HTTP request containing URL data
            
        Returns:
            Response containing shortened URL information or error
        """
        serializer = CreateShortenedURLSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Invalid input data",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get client IP address
            client_ip = self._get_client_ip(request)
            
            # Use service layer for business logic
            service = URLShortenerService()
            result = service.shorten_url(
                original_url=serializer.validated_data['original_url'],
                title=serializer.validated_data.get('title'),
                description=serializer.validated_data.get('description'),
                expires_at=serializer.validated_data.get('expires_at'),
                client_ip=client_ip
            )
            
            # Serialize the response
            response_serializer = ShortenedURLResponseSerializer(result)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except URLShortenerError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RedirectURLView(APIView):
    """
    API view for redirecting to original URLs.
    
    This view handles GET requests to redirect shortened URLs to their original URLs.
    It also tracks clicks and provides URL information.
    """
    
    @method_decorator(never_cache)
    @swagger_auto_schema(
        operation_description="Redirect to the original URL or get URL information",
        operation_summary="Redirect Shortened URL",
        operation_id="redirect_shortened_url",
        tags=["URL Redirection"],
        manual_parameters=[
            openapi.Parameter(
                'short_code',
                openapi.IN_PATH,
                description="The short code to redirect",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'info',
                openapi.IN_QUERY,
                description="Return URL information instead of redirecting",
                type=openapi.TYPE_BOOLEAN,
                default=False
            )
        ],
        responses={
            302: openapi.Response(description="Redirect to original URL"),
            200: openapi.Response(
                description="URL information (when info=true)",
                schema=RedirectResponseSerializer
            ),
            404: openapi.Response(
                description="Short URL not found",
                schema=ErrorSerializer
            ),
            410: openapi.Response(
                description="Short URL has expired",
                schema=ErrorSerializer
            )
        }
    )
    def get(self, request, short_code):
        """
        Redirect to original URL or return URL information.
        
        Args:
            request: HTTP request
            short_code: The short code to resolve
            
        Returns:
            HTTP redirect or JSON response with URL information
        """
        # Check if user wants info instead of redirect
        return_info = request.query_params.get('info', '').lower() == 'true'
        
        try:
            service = URLShortenerService()
            
            # Get URL information and track click
            url_data = service.get_original_url(
                short_code=short_code,
                track_click=not return_info  # Don't track clicks for info requests
            )
            
            # Track detailed click information if redirecting
            if not return_info:
                service.track_click(
                    short_code=short_code,
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    referer=request.META.get('HTTP_REFERER')
                )
            
            if return_info:
                # Return URL information as JSON
                serializer = RedirectResponseSerializer(url_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Redirect to original URL
                return HttpResponseRedirect(url_data['original_url'])
                
        except URLNotFoundError:
            return Response(
                {"error": f"Short URL '{short_code}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except URLExpiredError:
            return Response(
                {"error": f"Short URL '{short_code}' has expired"},
                status=status.HTTP_410_GONE
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class URLStatsView(APIView):
    """
    API view for retrieving URL statistics.
    
    This view provides detailed statistics about a shortened URL including
    click counts, creation date, expiration status, etc.
    """
    
    @swagger_auto_schema(
        operation_description="Get detailed statistics for a shortened URL",
        operation_summary="Get URL Statistics",
        operation_id="get_url_stats",
        tags=["URL Analytics"],
        manual_parameters=[
            openapi.Parameter(
                'short_code',
                openapi.IN_PATH,
                description="The short code to get statistics for",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="URL statistics retrieved successfully",
                schema=URLStatsSerializer
            ),
            404: openapi.Response(
                description="Short URL not found",
                schema=ErrorSerializer
            )
        }
    )
    def get(self, request, short_code):
        """
        Get statistics for a shortened URL.
        
        Args:
            request: HTTP request
            short_code: The short code to get stats for
            
        Returns:
            Response containing URL statistics
        """
        try:
            service = URLShortenerService()
            stats = service.get_url_stats(short_code)
            
            serializer = URLStatsSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except URLNotFoundError:
            return Response(
                {"error": f"Short URL '{short_code}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """
    API view for health check endpoint.
    
    This view provides a simple health check to verify the API is running.
    """
    
    @swagger_auto_schema(
        operation_description="Health check endpoint to verify API status",
        operation_summary="Health Check",
        operation_id="health_check",
        tags=["System"],
        responses={
            200: openapi.Response(
                description="API is healthy",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            )
        }
    )
    def get(self, request):
        """
        Health check endpoint.
        
        Returns:
            Response indicating API health status
        """
        from django.utils import timezone
        
        return Response({
            'status': 'healthy',
            'message': 'URL Shortener API is running',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK) 