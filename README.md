# URL Shortener API

A clean, efficient, and scalable URL shortening service built with Django REST Framework following clean architecture principles.

## 🚀 Features

- **URL Shortening**: Convert long URLs into short, shareable links
- **Custom Short Codes**: Reversible URL generation using Hashids
- **Analytics**: Track click counts and access statistics
- **Expiration Support**: Set expiration dates for shortened URLs
- **Class-Based Views**: Clean API design using DRF class-based views
- **Swagger Documentation**: Interactive API documentation

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
apps/shortener/
├── models.py          # Domain entities and business rules
├── services.py        # Business logic and use cases  
├── views.py          # Presentation layer (API endpoints)
├── serializers.py    # Data validation and transformation
├── exceptions.py     # Domain-specific exceptions
├── admin.py          # Django admin configuration
├── urls.py           # URL routing
└── tests.py          # Comprehensive test suite
```

### Architecture Layers

1. **Domain Layer** (`models.py`): Core business entities and rules
2. **Service Layer** (`services.py`): Application business logic and use cases
3. **Presentation Layer** (`views.py`): API endpoints and HTTP handling
4. **Infrastructure Layer**: Database, external services integration

## 📋 Requirements

- Python 3.11+
- See `requirements.txt` for complete dependencies

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd url-shortener
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file based on `env.example`:

```bash
cp env.example .env
```

Update the `.env` file with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DOMAIN=http://localhost:8000
HASHIDS_SALT=your-unique-salt-here
HASHIDS_MIN_LENGTH=6
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

## 🔌 API Endpoints

### Create Shortened URL

**POST** `/api/v1/shorten/`

```json
{
  "original_url": "https://www.example.com/very/long/url",
  "title": "Optional title",
  "description": "Optional description",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "short_code": "a1b2c3",
  "short_url": "http://localhost:8000/a1b2c3",
  "original_url": "https://www.example.com/very/long/url",
  "title": "Optional title",
  "description": "Optional description",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "click_count": 0
}
```

### Redirect to Original URL

**GET** `/{short_code}/`

Redirects to the original URL and tracks the click.

### Get URL Information

**GET** `/{short_code}/?info=true`

Returns URL information without redirecting:

```json
{
  "original_url": "https://www.example.com/very/long/url",
  "short_code": "a1b2c3",
  "title": "Optional title",
  "description": "Optional description"
}
```

### Get URL Statistics

**GET** `/api/v1/stats/{short_code}/`

```json
{
  "short_code": "a1b2c3",
  "original_url": "https://www.example.com/very/long/url",
  "title": "Optional title",
  "description": "Optional description",
  "click_count": 42,
  "created_at": "2024-01-15T10:30:00Z",
  "last_accessed_at": "2024-01-15T15:45:30Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "is_active": true,
  "is_expired": false
}
```

### Health Check

**GET** `/api/v1/health/`

```json
{
  "status": "healthy",
  "message": "URL Shortener API is running",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage

The project includes:
- Unit tests for models and services
- Integration tests for API endpoints
- Error handling tests
- Validation tests

## 🗄️ Database Schema

### ShortenedURL Model

- `original_url`: The original long URL
- `short_code`: Unique short code for the URL
- `title`: Optional title for the URL
- `description`: Optional description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `expires_at`: Optional expiration datetime
- `is_active`: Whether the URL is active
- `click_count`: Number of times accessed
- `last_accessed_at`: Last access timestamp
- `created_by_ip`: IP address that created the URL

### URLClick Model

- `shortened_url`: Foreign key to ShortenedURL
- `clicked_at`: Click timestamp
- `ip_address`: Clicker's IP address
- `user_agent`: Browser user agent
- `referer`: Referring URL

## 🔧 Configuration

### Settings

Key configuration options in `settings.py`:

```python
URL_SHORTENER = {
    'DOMAIN': 'http://localhost:8000',
    'HASHIDS_SALT': 'your-unique-salt',
    'HASHIDS_MIN_LENGTH': 6,
}
```

### Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DOMAIN`: Base domain for shortened URLs
- `HASHIDS_SALT`: Salt for generating short codes
- `HASHIDS_MIN_LENGTH`: Minimum length of short codes

## 🚀 Deployment

### Production Considerations

1. **Set DEBUG=False** in production
2. **Use a production database** (PostgreSQL recommended)
3. **Set up proper CORS headers** for frontend integration
4. **Configure HTTPS** for secure URLs
5. **Set up monitoring** and logging
6. **Use environment variables** for sensitive configuration

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🎯 Design Decisions

### Why Class-Based Views?

- **Object-oriented approach**: Better organization and reusability
- **DRF integration**: Natural fit with DRF's design patterns
- **Method separation**: Clear separation of HTTP methods
- **Simplicity**: No need for ViewSets and Routers in this simple use case

### Why Hashids for Short Codes?

- **Reversible**: Can decode back to original ID
- **URL-safe**: No confusing characters
- **Customizable**: Configurable length and alphabet
- **Secure**: Prevents enumeration attacks

## 🔍 Code Quality

The project maintains high code quality through:

- **Type hints**: Python type annotations where applicable
- **Clean code principles**: Following PEP 8 and Django best practices
- **Error handling**: Proper exception handling and user feedback
- **Input validation**: Comprehensive validation at multiple layers
- **Security considerations**: Protection against common vulnerabilities

## 📈 Performance Considerations

- **Database indexing**: Optimized database queries with proper indexes
- **Caching**: Ready for Redis/Memcached integration
- **Efficient lookups**: Fast short code resolution
- **Minimal dependencies**: Lightweight and fast startup

## 🛡️ Security Features

- **Input validation**: Comprehensive URL validation
- **IP tracking**: Request origin tracking for analytics
- **Expiration support**: URLs can have expiration dates
- **Admin interface**: Secure Django admin for management
- **CORS configuration**: Proper cross-origin request handling

## 📝 Notes

- It is not a high-performance service.
- Django settings are not production-ready.
- For production, we should add security feature, caching, logging, load balancing, monitoring etc.
- No sophisticated validation, safety measures, params cleaning, etc.
- Assumed we generate same short code for the same URL.
- We don't handle collisions.
- Add formatters and linters.
- Missing some tests.

## TODO
- [ ] Add tests
- [ ] Add logging
- [ ] Add monitoring
- [ ] Add CI/CD
- [ ] Add documentation
- [ ] Add metrics
- [ ] Add tracing
- [ ] Add Django Configurations
- [ ] Add linting and formatting