#!/usr/bin/env python3
"""
Enhanced Review Scraper - Main CLI Application with Demo Mode

This script scrapes product reviews from G2, Capterra, and Software Advice
for a specific company and time period. Includes demo mode for testing.
"""

import click
import json
import logging
from datetime import datetime
from g2_scraper import G2Scraper
from capterra_scraper import CapterraScraper
from software_advice_scraper import SoftwareAdviceScraper
from utils import setup_logging, save_reviews_to_json, validate_date_format, parse_date

# Set up logging
logger = setup_logging()

# Available sources
SOURCES = ['g2', 'capterra', 'software-advice', 'all']

def validate_inputs(company_name, start_date, end_date, source):
    """Validate input parameters"""
    if not company_name or not company_name.strip():
        raise ValueError("Company name cannot be empty")
    
    if not validate_date_format(start_date):
        raise ValueError("Start date must be in YYYY-MM-DD format")
    
    if not validate_date_format(end_date):
        raise ValueError("End date must be in YYYY-MM-DD format")
    
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    if start_dt > end_dt:
        raise ValueError("Start date must be before or equal to end date")
    
    if start_dt > datetime.now():
        raise ValueError("Start date cannot be in the future")
    
    if end_dt > datetime.now():
        raise ValueError("End date cannot be in the future")
    
    if source.lower() not in SOURCES:
        raise ValueError(f"Source must be one of: {', '.join(SOURCES)}")

def generate_demo_reviews(company_name, start_date, end_date, source):
    """Generate demo reviews for testing purposes"""
    demo_reviews = [
        {
            "title": f"Excellent {company_name} Platform",
            "description": f"{company_name} has transformed our business operations completely. The features are outstanding and the integration capabilities are seamless. Customer support is very responsive and helpful.",
            "date": "2023-08-15",
            "reviewer_name": "John Smith",
            "rating": 5,
            "helpful_votes": "24",
            "source": "G2"
        },
        {
            "title": f"Powerful but Complex {company_name}",
            "description": f"Great features from {company_name} but requires significant training. The learning curve is steep but worth it once you get the hang of it. Customization options are extensive.",
            "date": "2023-09-28",
            "reviewer_name": "Sarah Johnson",
            "rating": 4,
            "helpful_votes": "18",
            "source": "Capterra"
        },
        {
            "title": f"Best Investment for Our Team - {company_name}",
            "description": f"{company_name}'s platform has streamlined our workflow significantly. The pricing is reasonable and the ROI has been excellent. Highly recommend for growing businesses.",
            "date": "2023-11-02",
            "reviewer_name": "Mike Chen",
            "rating": 5,
            "helpful_votes": "31",
            "source": "Software Advice"
        },
        {
            "title": f"Good Tool with Room for Improvement - {company_name}",
            "description": f"Solid platform from {company_name} with good core functionality. Some advanced features feel clunky and the reporting could be more robust. Overall satisfied with the value for money.",
            "date": "2023-07-20",
            "reviewer_name": "Lisa Rodriguez",
            "rating": 3.5,
            "helpful_votes": "12",
            "source": "G2"
        },
        {
            "title": f"Outstanding Customer Service from {company_name}",
            "description": f"What sets {company_name} apart is their exceptional customer service. Whenever we've had issues, their support team has been quick to respond and resolve problems effectively.",
            "date": "2023-10-10",
            "reviewer_name": "David Wilson",
            "rating": 4.5,
            "helpful_votes": "27",
            "source": "Capterra"
        }
    ]
    
    # Filter by source
    if source != 'all':
        source_mapping = {
            'g2': 'G2',
            'capterra': 'Capterra',
            'software-advice': 'Software Advice'
        }
        target_source = source_mapping.get(source, source)
        demo_reviews = [r for r in demo_reviews if r['source'] == target_source]
    
    # Filter by date range
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    filtered_reviews = []
    for review in demo_reviews:
        review_date = parse_date(review['date'])
        if start_dt <= review_date <= end_dt:
            filtered_reviews.append(review)
    
    return filtered_reviews

def scrape_reviews(company_name, start_date, end_date, source, demo_mode=False):
    """Scrape reviews from the specified source"""
    all_reviews = []
    
    if demo_mode:
        logger.info("Running in DEMO MODE - generating sample reviews")
        return generate_demo_reviews(company_name, start_date, end_date, source)
    
    if source == 'all':
        sources_to_scrape = ['g2', 'capterra', 'software-advice']
    else:
        sources_to_scrape = [source]
    
    for src in sources_to_scrape:
        logger.info(f"Scraping reviews from {src}...")
        
        try:
            if src == 'g2':
                scraper = G2Scraper()
                reviews = scraper.get_reviews(company_name, start_date, end_date)
            elif src == 'capterra':
                scraper = CapterraScraper()
                reviews = scraper.get_reviews(company_name, start_date, end_date)
            elif src == 'software-advice':
                scraper = SoftwareAdviceScraper()
                reviews = scraper.get_reviews(company_name, start_date, end_date)
            
            logger.info(f"Collected {len(reviews)} reviews from {src}")
            all_reviews.extend(reviews)
            
        except Exception as e:
            logger.error(f"Error scraping from {src}: {e}")
            continue
    
    return all_reviews

@click.command()
@click.option('--company-name', '-c', required=True, help='Name of the company to scrape reviews for')
@click.option('--start-date', '-s', required=True, help='Start date in YYYY-MM-DD format')
@click.option('--end-date', '-e', required=True, help='End date in YYYY-MM-DD format')
@click.option('--source', '-src', default='all', 
              type=click.Choice(SOURCES, case_sensitive=False),
              help='Source to scrape reviews from (default: all)')
@click.option('--output', '-o', help='Output file name (optional)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--demo', '-d', is_flag=True, help='Run in demo mode (generate sample data)')
def main(company_name, start_date, end_date, source, output, verbose, demo):
    """
    Review Scraper - Scrape product reviews from G2, Capterra, and Software Advice
    
    Example usage:
    python review_scraper.py -c "Salesforce" -s "2023-01-01" -e "2023-12-31" -src g2
    python review_scraper.py -c "HubSpot" -s "2023-06-01" -e "2023-12-31" --verbose --demo
    """
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("Review Scraper Started")
    logger.info("=" * 60)
    logger.info(f"Company: {company_name}")
    logger.info(f"Date Range: {start_date} to {end_date}")
    logger.info(f"Source: {source}")
    if demo:
        logger.info("MODE: DEMO MODE (Sample Data)")
    else:
        logger.info("MODE: Live Scraping")
    logger.info("-" * 60)
    
    try:
        # Validate inputs
        validate_inputs(company_name, start_date, end_date, source)
        
        # Scrape reviews
        logger.info("Starting review scraping...")
        reviews = scrape_reviews(company_name, start_date, end_date, source, demo_mode=demo)
        
        if not reviews:
            logger.warning("No reviews found for the specified criteria")
            return
        
        logger.info(f"Total reviews collected: {len(reviews)}")
        
        # Save to JSON file
        if output:
            filename = output
            # Create output directory if it doesn't exist
            import os
            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, indent=2, ensure_ascii=False)
        else:
            filename = save_reviews_to_json(reviews, company_name, source)
        
        logger.info(f"Reviews saved to: {filename}")
        
        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("SCRAPING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Company: {company_name}")
        logger.info(f"Date Range: {start_date} to {end_date}")
        logger.info(f"Source(s): {source}")
        logger.info(f"Total Reviews: {len(reviews)}")
        logger.info(f"Mode: {'Demo' if demo else 'Live'}")
        
        # Group by source for summary
        if reviews:
            from collections import Counter
            source_counts = Counter(review.get('source', 'Unknown') for review in reviews)
            logger.info("Reviews by source:")
            for src, count in source_counts.items():
                logger.info(f"  {src}: {count}")
        
        logger.info(f"Output file: {filename}")
        logger.info("=" * 60)
        
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        raise click.BadParameter(str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise click.ClickException(f"An error occurred: {e}")

if __name__ == '__main__':
    main()