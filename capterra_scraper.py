import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import logging
from urllib.parse import urljoin, quote_plus
from config import CAPTERA_BASE_URL, CAPTERA_SEARCH_URL, CAPTERA_REVIEWS_PER_PAGE, REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS, MAX_RETRIES
from utils import parse_date

logger = logging.getLogger(__name__)

class CapterraScraper:
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
        """Search for company on Capterra and return the product URL"""
        search_url = CAPTERRA_SEARCH_URL.format(company_name=quote_plus(company_name))
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(search_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for product links in search results
                product_links = soup.find_all('a', class_='ProductTile__ProductName-sc-1dje9l3-6')
                
                for link in product_links:
                    if company_name.lower() in link.text.lower():
                        product_url = urljoin(CAPTERA_BASE_URL, link['href'])
                        logger.info(f"Found Capterra product page: {product_url}")
                        return product_url
                
                # Alternative search for product cards
                product_cards = soup.find_all('div', class_='ProductTile')
                for card in product_cards:
                    link = card.find('a', class_='ProductTile__ProductName')
                    if link and company_name.lower() in link.text.lower():
                        product_url = urljoin(CAPTERA_BASE_URL, link['href'])
                        logger.info(f"Found Capterra product page: {product_url}")
                        return product_url
                
                logger.warning(f"Company '{company_name}' not found in Capterra search results")
                return None
                
            except requests.RequestException as e:
                logger.error(f"Error searching Capterra for company (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(DELAY_BETWEEN_REQUESTS * (attempt + 1))
                continue
        
        return None
    
    def get_reviews(self, company_name, start_date, end_date):
        """Scrape reviews from Capterra for a specific company and date range"""
        logger.info(f"Starting Capterra review scraping for {company_name}")
        
        # Search for the company first
        product_url = self.search_company(company_name)
        if not product_url:
            logger.error(f"Could not find Capterra page for company: {company_name}")
            return []
        
        # Navigate to reviews page
        reviews_url = f"{product_url}/reviews"
        all_reviews = []
        page = 1
        
        start_datetime = parse_date(start_date)
        end_datetime = parse_date(end_date)
        
        while True:
            try:
                page_url = f"{reviews_url}?page={page}"
                logger.info(f"Fetching Capterra reviews page {page}: {page_url}")
                
                response = self.session.get(page_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find review containers - Capterra uses different class names
                review_elements = soup.find_all('div', class_='ReviewCard')
                
                if not review_elements:
                    # Try alternative class names
                    review_elements = soup.find_all('div', class_='review-card')
                    if not review_elements:
                        review_elements = soup.find_all('article', class_='review')
                
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
                    # Try alternative pagination
                    next_button = soup.find('button', class_='pagination-next')
                    if not next_button or next_button.get('disabled'):
                        logger.info("No more pages available")
                        break
                
                page += 1
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
            except requests.RequestException as e:
                logger.error(f"Error fetching Capterra reviews page {page}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error parsing Capterra reviews: {e}")
                break
        
        logger.info(f"Total Capterra reviews collected: {len(all_reviews)}")
        return all_reviews
    
    def parse_review(self, review_element):
        """Parse individual review element"""
        try:
            # Extract review title
            title_element = review_element.find('h3', class_='ReviewCard__Title')
            if not title_element:
                title_element = review_element.find('h4', class_='review-title')
            title = title_element.text.strip() if title_element else "No Title"
            
            # Extract review content
            content_element = review_element.find('div', class_='ReviewCard__Description')
            if not content_element:
                content_element = review_element.find('div', class_='review-content')
            if not content_element:
                content_element = review_element.find('p', class_='review-text')
            content = content_element.text.strip() if content_element else ""
            
            # Extract review date
            date_element = review_element.find('time')
            if date_element and date_element.get('datetime'):
                date = date_element['datetime'][:10]
            else:
                # Try alternative date extraction
                date_element = review_element.find('span', class_='ReviewCard__Date')
                if not date_element:
                    date_element = review_element.find('div', class_='review-date')
                if date_element:
                    date_text = date_element.text.strip()
                    # Try to parse various date formats
                    try:
                        # Handle relative dates like "2 months ago"
                        if 'ago' in date_text.lower():
                            from dateutil.relativedelta import relativedelta
                            import re
                            
                            match = re.search(r'(\d+)\s+(\w+)\s+ago', date_text.lower())
                            if match:
                                amount, unit = match.groups()
                                amount = int(amount)
                                
                                if 'month' in unit:
                                    review_date = datetime.now() - relativedelta(months=amount)
                                elif 'year' in unit:
                                    review_date = datetime.now() - relativedelta(years=amount)
                                elif 'day' in unit:
                                    review_date = datetime.now() - relativedelta(days=amount)
                                elif 'week' in unit:
                                    review_date = datetime.now() - relativedelta(weeks=amount)
                                else:
                                    review_date = datetime.now()
                                
                                date = review_date.strftime('%Y-%m-%d')
                            else:
                                date = datetime.now().strftime('%Y-%m-%d')
                        else:
                            # Try to parse as regular date
                            try:
                                parsed_date = datetime.strptime(date_text, '%b %d, %Y')
                                date = parsed_date.strftime('%Y-%m-%d')
                            except:
                                date = datetime.now().strftime('%Y-%m-%d')
                    except:
                        date = datetime.now().strftime('%Y-%m-%d')
                else:
                    date = datetime.now().strftime('%Y-%m-%d')
            
            # Extract reviewer name
            reviewer_element = review_element.find('span', class_='ReviewCard__ReviewerName')
            if not reviewer_element:
                reviewer_element = review_element.find('div', class_='reviewer-name')
            if not reviewer_element:
                reviewer_element = review_element.find('span', class_='reviewer__name')
            reviewer_name = reviewer_element.text.strip() if reviewer_element else "Anonymous"
            
            # Extract rating
            rating = 0
            rating_element = review_element.find('div', class_='ReviewCard__Rating')
            if not rating_element:
                rating_element = review_element.find('div', class_='rating')
            
            if rating_element:
                # Look for filled stars or rating numbers
                stars = rating_element.find_all('svg', class_='star-filled')
                if stars:
                    rating = len(stars)
                else:
                    # Try to find rating text like "4.5/5"
                    rating_text = rating_element.text.strip()
                    if '/' in rating_text:
                        try:
                            rating = float(rating_text.split('/')[0])
                        except:
                            rating = 0
            
            # Extract helpful votes
            helpful_element = review_element.find('span', class_='ReviewCard__HelpfulCount')
            if not helpful_element:
                helpful_element = review_element.find('span', class_='helpful-count')
            helpful_votes = helpful_element.text.strip() if helpful_element else "0"
            
            return {
                'title': title,
                'description': content,
                'date': date,
                'reviewer_name': reviewer_name,
                'rating': rating,
                'helpful_votes': helpful_votes,
                'source': 'Capterra'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Capterra review: {e}")
            return None