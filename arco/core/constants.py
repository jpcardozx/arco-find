"""
ARCO Constants - Configurações e constantes do sistema
"""

# Version
VERSION = "2.0"

# Cache settings
DOMAIN_CACHE_SIZE = 1000
RESULTS_CACHE_SIZE = 500
PAGESPEED_CACHE_SIZE = 300
VALIDATION_CACHE_SIZE = 200

# Rate limiting
API_RATE_LIMIT = 10  # requests per second
DEFAULT_CALLS_PER_SECOND = 2.0
RETRY_DELAY = 2  # seconds
RETRY_DELAY_MULTIPLIER = 1.5
MAX_BACKOFF_MULTIPLIER = 8.0
SUCCESS_STREAK_THRESHOLD = 5
RATE_LIMIT_ACCELERATION_FACTOR = 0.8

# Processing limits
MAX_CONCURRENT_REQUESTS = 5
BATCH_SIZE = 50

# API settings
DEFAULT_API_TIMEOUT = 30
DEFAULT_QUALIFICATION_THRESHOLD = 65.0

# Domain validation
MIN_DOMAIN_LENGTH = 4
MAX_DOMAIN_LENGTH = 100
DOMAIN_PATTERN = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
SUSPICIOUS_DOMAIN_KEYWORDS = ['test', 'example', 'demo', 'temp']

# Quality thresholds
MIN_CONFIDENCE_SCORE = 0.7
MIN_RELEVANCE_SCORE = 0.6

# Business metrics
TARGET_MONTHLY_SPEND_MIN = 5000  # USD
HIGH_VALUE_SPEND_THRESHOLD = 25000  # USD

# Geographic markets
SUPPORTED_MARKETS = ['US', 'UK', 'CA', 'AU', 'NZ', 'SE', 'SG']

# Industry verticals
SUPPORTED_VERTICALS = [
    'legal', 'dental', 'restaurants', 'fitness', 
    'real_estate', 'automotive', 'medical', 'home_services'
]

# API endpoints
SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"
PAGESPEED_BASE_URL = "https://www.googleapis.com/pagespeed/insights/v5/runPagespeed"

# Error handling
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
