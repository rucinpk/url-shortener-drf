"""
Tests for URL shortener application.
Following clean architecture principles with unit and integration tests.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from unittest.mock import patch

from .models import ShortenedURL
from .services import URLShortenerService
from .exceptions import URLShortenerError, URLNotFoundError, URLExpiredError


class ShortenedURLModelTests(TestCase):
    """Test cases for ShortenedURL model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_url = "https://www.example.com/very/long/url/that/needs/shortening"
        
    def test_create_shortened_url(self):
        """Test creating a shortened URL."""
        url = ShortenedURL.objects.create(
            original_url=self.valid_url,
            short_code="abc123",
            title="Test URL"
        )
        
        self.assertEqual(url.original_url, self.valid_url)
        self.assertEqual(url.short_code, "abc123")
        self.assertEqual(url.title, "Test URL")
        self.assertTrue(url.is_active)
        self.assertEqual(url.click_count, 0)
        

    def test_increment_click_count(self):
        """Test incrementing click count."""
        url = ShortenedURL.objects.create(
            original_url=self.valid_url,
            short_code="abc123"
        )
        
        initial_count = url.click_count
        url.increment_click_count()
        
        # Refresh from database
        url.refresh_from_db()
        self.assertEqual(url.click_count, initial_count + 1)
        self.assertIsNotNone(url.last_accessed_at)


class URLShortenerServiceTests(TestCase):
    """Test cases for URLShortenerService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = URLShortenerService()
        self.valid_url = "https://www.example.com/test"
        
    def test_shorten_url_success(self):
        """Test successful URL shortening."""
        result = self.service.shorten_url(self.valid_url, title="Test URL")
        
        self.assertIn('short_code', result)
        self.assertIn('short_url', result)
        self.assertEqual(result['original_url'], self.valid_url)
        self.assertEqual(result['title'], "Test URL")
        self.assertGreater(len(result['short_code']), 0)
        
    def test_shorten_invalid_url(self):
        """Test shortening invalid URL."""
        with self.assertRaises(URLShortenerError):
            self.service.shorten_url("invalid-url")
            
    def test_get_original_url_success(self):
        """Test successful URL retrieval."""
        # First create a shortened URL
        result = self.service.shorten_url(self.valid_url)
        short_code = result['short_code']
        
        # Then retrieve it
        retrieved = self.service.get_original_url(short_code)
        
        self.assertEqual(retrieved['original_url'], self.valid_url)
        self.assertEqual(retrieved['short_code'], short_code)
        
    def test_get_nonexistent_url(self):
        """Test retrieving non-existent URL."""
        with self.assertRaises(URLNotFoundError):
            self.service.get_original_url("nonexistent")
            
    def test_get_url_stats(self):
        """Test getting URL statistics."""
        result = self.service.shorten_url(self.valid_url, title="Test")
        short_code = result['short_code']
        
        stats = self.service.get_url_stats(short_code)
        
        self.assertEqual(stats['short_code'], short_code)
        self.assertEqual(stats['original_url'], self.valid_url)
        self.assertEqual(stats['title'], "Test")
        self.assertEqual(stats['click_count'], 0)


class URLShortenerAPITests(APITestCase):
    """Integration tests for URL shortener API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_url = "https://www.example.com/test"
        self.create_url = reverse('shortener:create_shortened_url')
        
    def test_create_shortened_url_success(self):
        """Test successful URL creation via API."""
        data = {
            'original_url': self.valid_url,
            'title': 'Test URL'
        }
        
        response = self.client.post(self.create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('short_code', response.data)
        self.assertIn('short_url', response.data)
        self.assertEqual(response.data['original_url'], self.valid_url)
        self.assertEqual(response.data['title'], 'Test URL')
        
    def test_create_shortened_url_invalid_data(self):
        """Test URL creation with invalid data."""
        data = {
            'original_url': 'invalid-url'
        }
        
        response = self.client.post(self.create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
            
    def test_health_check(self):
        """Test health check endpoint."""
        health_url = reverse('shortener:health_check')
        response = self.client.get(health_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('timestamp', response.data)