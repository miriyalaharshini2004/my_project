import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import logging
from urllib.parse import urljoin, quote_plus
from config import G2_BASE_URL, G2_SEARCH_URL, G2_REVIEWS_PER_PAGE, REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS, MAX_RETRIES
from utils import parse_date

logger = logging.getLogger(__name__)

class G2Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_company(self, company_name):
        """Search for company on G2 and return the product URL"""
        search_url = G2_SEARCH_URL.format(company_name=quote_plus(company_name))
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(search_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for product links in search results
                product_links = soup.find_all('a', class_='link--header-color')
                
                for link in product_links:
                    if company_name.lower() in link.text.lower():
                        product_url = urljoin(G2_BASE_URL, link['href'])
                        logger.info(f"Found G2 product page: {product_url}")
                        return product_url
                
                # Alternative search for product cards
                product_cards = soup.find_all('div', class_='product-card')
                for card in product_cards:
                    link = card.find('a', class_='product-card__name')
                    if link and company_name.lower() in link.text.lower():
                        product_url = urljoin(G2_BASE_URL, link['href'])
                        logger.info(f"Found G2 product page: {product_url}")
                        return product_url
                
                logger.warning(f"Company '{company_name}' not found in G2 search results")
                return None
                
            except requests.RequestException as e:
                logger.error(f"Error searching G2 for company (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(DELAY_BETWEEN_REQUESTS * (attempt + 1))
                continue
        
        return None
    
    def get_reviews(self, company_name, start_date, end_date):
        """Scrape reviews from G2 for a specific company and date range"""
        logger.info(f"Starting G2 review scraping for {company_name}")
        
        # Search for the company first
        product_url = self.search_company(company_name)
        if not product_url:
            logger.error(f"Could not find G2 page for company: {company_name}")
            return []
        
        reviews_url = f"{product_url}/reviews"
        all_reviews = []
        page = 1
        
        start_datetime = parse_date(start_date)
        end_datetime = parse_date(end_date)
        
        while True:
            try:
                page_url = f"{reviews_url}?page={page}"
                logger.info(f"Fetching G2 reviews page {page}: {page_url}")
                
                response = self.session.get(page_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find review containers
                review_elements = soup.find_all('div', class_='review')
                
                if not review_elements:
                    logger.info(f"No more reviews found on page {page}")
                    break
                
                for review_element in review_elements:
                    review_data = self.parse_review(review_element)
                    
                    if review_data:
                        review_date = parse_date(review_data['date'])
                        
                        # Check if review is within date range
                        if start_datetime <= review_date <= end_datetime:
                            all_reviews.append(review_data)
                            logger.info(f"Added review from {review_data['date']}")
                        elif review_date < start_datetime:
                            # If we've gone past the start date, we can stop
                            logger.info(f"Reached reviews older than start date, stopping")
                            return all_reviews
                
                # Check if there's a next page
                next_button = soup.find('a', class_='pagination__next')
                if not next_button or 'disabled' in next_button.get('class', []):
                    logger.info("No more pages available")
                    break
                
                page += 1
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
            except requests.RequestException as e:
                logger.error(f"Error fetching G2 reviews page {page}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error parsing G2 reviews: {e}")
                break
        
        logger.info(f"Total G2 reviews collected: {len(all_reviews)}")
        return all_reviews
    
    def parse_review(self, review_element):
        """Parse individual review element"""
        try:
            # Extract review title
            title_element = review_element.find('h3', class_='review__title')
            title = title_element.text.strip() if title_element else "No Title"
            
            # Extract review content
            content_element = review_element.find('div', class_='review__content')
            content = content_element.text.strip() if content_element else ""
            
            # Extract review date
            date_element = review_element.find('time')
            if date_element and date_element.get('datetime'):
                date = date_element['datetime'][:10]  # Get YYYY-MM-DD part
            else:
                # Try alternative date extraction
                date_element = review_element.find('div', class_='review__date')
                date = date_element.text.strip() if date_element else datetime.now().strftime('%Y-%m-%d')
            
            # Extract reviewer name
            reviewer_element = review_element.find('div', class_='reviewer__name')
            reviewer_name = reviewer_element.text.strip() if reviewer_element else "Anonymous"
            
            # Extract rating
            rating_element = review_element.find('div', class_='review__rating')
            rating = 0
            if rating_element:
                stars = rating_element.find_all('svg', class_='star')
                filled_stars = len([star for star in stars if 'filled' in star.get('class', [])])
                rating = filled_stars
            
            # Extract helpful votes
            helpful_element = review_element.find('span', class_='review__helpful-count')
            helpful_votes = helpful_element.text.strip() if helpful_element else "0"
            
            return {
                'title': title,
                'description': content,
                'date': date,
                'reviewer_name': reviewer_name,
                'rating': rating,
                'helpful_votes': helpful_votes,
                'source': 'G2'
            }
            
        except Exception as e:
            logger.error(f"Error parsing G2 review: {e}")
            return None