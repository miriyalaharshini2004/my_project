import logging
import os
from datetime import datetime
from config import LOG_FILE, OUTPUT_DIR

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_output_directory():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def save_reviews_to_json(reviews, company_name, source):
    """Save reviews to JSON file"""
    create_output_directory()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{OUTPUT_DIR}/{company_name}_{source}_reviews_{timestamp}.json"
    
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    
    return filename

def validate_date_format(date_string):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def parse_date(date_string):
    """Parse date string to datetime object"""
    return datetime.strptime(date_string, '%Y-%m-%d')