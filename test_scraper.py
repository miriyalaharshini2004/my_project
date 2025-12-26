#!/usr/bin/env python3
"""
Test script for the review scraper
"""

import json
import logging
from datetime import datetime
from utils import validate_date_format, parse_date, save_reviews_to_json

def test_date_validation():
    """Test date validation functions"""
    print("Testing date validation...")
    
    # Valid dates
    assert validate_date_format("2023-01-01") == True
    assert validate_date_format("2023-12-31") == True
    assert validate_date_format("2024-02-29") == True  # Leap year
    
    # Invalid dates
    assert validate_date_format("2023-13-01") == False  # Invalid month
    assert validate_date_format("2023-01-32") == False  # Invalid day
    assert validate_date_format("2023-01-01T00:00:00") == False  # Invalid format
    assert validate_date_format("01-01-2023") == False  # Wrong order
    
    # Date parsing
    dt = parse_date("2023-06-15")
    assert dt.year == 2023
    assert dt.month == 6
    assert dt.day == 15
    
    print("✓ Date validation tests passed")

def test_json_output():
    """Test JSON output generation"""
    print("Testing JSON output generation...")
    
    sample_reviews = [
        {
            "title": "Excellent Test Platform",
            "description": "This is a test review with detailed content about the platform.",
            "date": "2023-08-15",
            "reviewer_name": "Test User",
            "rating": 5,
            "helpful_votes": "24",
            "source": "G2"
        },
        {
            "title": "Good Tool with Room for Improvement",
            "description": "Solid platform with good core functionality. Some features could be improved.",
            "date": "2023-07-20",
            "reviewer_name": "Jane Doe",
            "rating": 3.5,
            "helpful_votes": "12",
            "source": "Capterra"
        }
    ]
    
    filename = save_reviews_to_json(sample_reviews, "TestCompany", "g2")
    
    # Verify file was created
    import os
    assert os.path.exists(filename)
    
    # Verify JSON content
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) == 2
    assert data[0]['title'] == "Excellent Test Platform"
    assert data[0]['source'] == "G2"
    assert data[1]['rating'] == 3.5
    
    print(f"✓ JSON output test passed - saved to {filename}")

def test_demo_mode():
    """Test demo mode functionality"""
    print("Testing demo mode...")
    
    # Import the demo function from main script
    from review_scraper import generate_demo_reviews
    
    # Test demo reviews generation
    demo_reviews = generate_demo_reviews("TestCompany", "2023-01-01", "2023-12-31", "all")
    
    assert len(demo_reviews) > 0
    assert all('title' in review for review in demo_reviews)
    assert all('description' in review for review in demo_reviews)
    assert all('date' in review for review in demo_reviews)
    assert all('rating' in review for review in demo_reviews)
    assert all('source' in review for review in demo_reviews)
    
    # Test source filtering
    g2_reviews = generate_demo_reviews("TestCompany", "2023-01-01", "2023-12-31", "g2")
    assert all(review['source'] == 'G2' for review in g2_reviews)
    
    capterra_reviews = generate_demo_reviews("TestCompany", "2023-01-01", "2023-12-31", "capterra")
    assert all(review['source'] == 'Capterra' for review in capterra_reviews)
    
    print("✓ Demo mode tests passed")

def test_sample_json_generation():
    """Generate a sample JSON file for demonstration"""
    print("Generating sample JSON output...")
    
    sample_reviews = [
        {
            "title": "Excellent Salesforce Platform",
            "description": "Salesforce has transformed our business operations completely. The features are outstanding and the integration capabilities are seamless. Customer support is very responsive and helpful.",
            "date": "2023-08-15",
            "reviewer_name": "John Smith",
            "rating": 5,
            "helpful_votes": "24",
            "source": "G2"
        },
        {
            "title": "Powerful but Complex Salesforce",
            "description": "Great features from Salesforce but requires significant training. The learning curve is steep but worth it once you get the hang of it. Customization options are extensive.",
            "date": "2023-09-28",
            "reviewer_name": "Sarah Johnson",
            "rating": 4,
            "helpful_votes": "18",
            "source": "Capterra"
        },
        {
            "title": "Best Investment for Our Team - Salesforce",
            "description": "Salesforce's platform has streamlined our workflow significantly. The pricing is reasonable and the ROI has been excellent. Highly recommend for growing businesses.",
            "date": "2023-11-02",
            "reviewer_name": "Mike Chen",
            "rating": 5,
            "helpful_votes": "31",
            "source": "Software Advice"
        },
        {
            "title": "Good Tool with Room for Improvement - Salesforce",
            "description": "Solid platform from Salesforce with good core functionality. Some advanced features feel clunky and the reporting could be more robust. Overall satisfied with the value for money.",
            "date": "2023-07-20",
            "reviewer_name": "Lisa Rodriguez",
            "rating": 3.5,
            "helpful_votes": "12",
            "source": "G2"
        },
        {
            "title": "Outstanding Customer Service from Salesforce",
            "description": "What sets Salesforce apart is their exceptional customer service. Whenever we've had issues, their support team has been quick to respond and resolve problems effectively.",
            "date": "2023-10-10",
            "reviewer_name": "David Wilson",
            "rating": 4.5,
            "helpful_votes": "27",
            "source": "Capterra"
        }
    ]
    
    filename = save_reviews_to_json(sample_reviews, "Salesforce", "all")
    print(f"✓ Sample JSON generated: {filename}")
    
    # Display the generated JSON content
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\nSample JSON content:")
    print(content[:500] + "..." if len(content) > 500 else content)

def main():
    """Run all tests"""
    print("=" * 60)
    print("Review Scraper Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        test_date_validation()
        test_json_output()
        test_demo_mode()
        test_sample_json_generation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe review scraper is ready to use!")
        print("\nTry these commands:")
        print('  python review_scraper.py -c "Salesforce" -s "2023-01-01" -e "2023-12-31" --demo')
        print('  python review_scraper.py -c "HubSpot" -s "2023-06-01" -e "2023-12-31" -src g2 --demo')
        print('  python review_scraper.py --help')
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()