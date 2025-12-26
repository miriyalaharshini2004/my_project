# Review Scraper Configuration
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
DELAY_BETWEEN_REQUESTS = 2

# G2 Configuration
G2_BASE_URL = 'https://www.g2.com'
G2_SEARCH_URL = 'https://www.g2.com/search?query={company_name}'
G2_REVIEWS_PER_PAGE = 25

# Capterra Configuration
CAPTERA_BASE_URL = 'https://www.capterra.com'
CAPTERA_SEARCH_URL = 'https://www.capterra.com/search/?search={company_name}'
CAPTERA_REVIEWS_PER_PAGE = 10

# Software Advice Configuration (Third Source)
SOFTWARE_ADVICE_BASE_URL = 'https://www.softwareadvice.com'
SOFTWARE_ADVICE_SEARCH_URL = 'https://www.softwareadvice.com/search/?q={company_name}'
SOFTWARE_ADVICE_REVIEWS_PER_PAGE = 10

# Output Configuration
OUTPUT_DIR = 'output'
LOG_FILE = 'review_scraper.log'
MAX_REVIEWS_PER_SOURCE = 1000