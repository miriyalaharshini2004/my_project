# SaaS Review Scraper

A Python script to scrape product reviews from G2, Capterra, and Software Advice for specific companies and time periods. This tool helps collect structured review data for competitive analysis, market research, and customer feedback analysis.

## Features

- **Multi-Platform Support**: Scrapes reviews from G2, Capterra, and Software Advice
- **Date Range Filtering**: Filter reviews by specific date ranges
- **Demo Mode**: Generate sample data for testing and development
- **Comprehensive Output**: Structured JSON format with review details
- **Error Handling**: Robust error handling and logging
- **Rate Limiting**: Respectful scraping with delays between requests
- **CLI Interface**: Easy-to-use command-line interface

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Scrape reviews for a company from all sources
python review_scraper.py -c "Salesforce" -s "2023-01-01" -e "2023-12-31"

# Scrape reviews from a specific source
python review_scraper.py -c "HubSpot" -s "2023-06-01" -e "2023-12-31" -src g2

# Use demo mode for testing
python review_scraper.py -c "Salesforce" -s "2023-01-01" -e "2023-12-31" --demo
```

### Command Line Options

- `-c, --company-name`: Name of the company to scrape reviews for (required)
- `-s, --start-date`: Start date in YYYY-MM-DD format (required)
- `-e, --end-date`: End date in YYYY-MM-DD format (required)
- `-src, --source`: Source to scrape from (g2, capterra, software-advice, or all; default: all)
- `-o, --output`: Custom output file name (optional)
- `-v, --verbose`: Enable verbose logging
- `-d, --demo`: Run in demo mode (generates sample data)

### Examples

```bash
# Scrape all reviews for Salesforce in 2023
python review_scraper.py -c "Salesforce" -s "2023-01-01" -e "2023-12-31"

# Scrape only G2 reviews for HubSpot with verbose output
python review_scraper.py -c "HubSpot" -s "2023-01-01" -e "2023-12-31" -src g2 --verbose

# Generate demo data for testing
python review_scraper.py -c "TestCompany" -s "2023-01-01" -e "2023-12-31" --demo

# Save output to custom file
python review_scraper.py -c "Salesforce" -s "2023-01-01" -e "2023-12-31" -o "my_reviews.json"
```

## Demo Mode

The demo mode generates realistic sample review data for testing purposes. This is useful when:
- Testing the script functionality
- Developing integrations
- Demonstrating the tool without hitting rate limits
- Working in environments where live scraping is restricted

To use demo mode, simply add the `--demo` flag to any command.

## Output Format

The script outputs JSON files with the following structure:

```json
[
  {
    "title": "Excellent Salesforce Platform",
    "description": "Salesforce has transformed our business operations completely...",
    "date": "2023-08-15",
    "reviewer_name": "John Smith",
    "rating": 5,
    "helpful_votes": "24",
    "source": "G2"
  },
  {
    "title": "Powerful but Complex Salesforce",
    "description": "Great features from Salesforce but requires significant training...",
    "date": "2023-09-28",
    "reviewer_name": "Sarah Johnson",
    "rating": 4,
    "helpful_votes": "18",
    "source": "Capterra"
  }
]
```

Each review contains:
- **title**: Review title/headline
- **description**: Full review text
- **date**: Review posting date (YYYY-MM-DD format)
- **reviewer_name**: Name of the reviewer (when available)
- **rating**: Numeric rating (1-5 scale)
- **helpful_votes**: Number of helpful votes
- **source**: Platform where the review was found

## Third Source: Software Advice

As a bonus feature, this script includes integration with **Software Advice** (softwareadvice.com), a specialized platform for SaaS software reviews. Software Advice focuses specifically on business software and provides:

- Detailed software comparisons
- Industry-specific recommendations
- Expert reviews and buyer guides
- User-generated reviews with ratings

This third source complements G2 and Capterra by providing additional perspectives and potentially different user demographics.

## Anti-Bot Measures and Limitations

Please note that review platforms implement various anti-scraping measures:

- **Rate limiting**: The script includes delays between requests
- **IP blocking**: Some platforms may block repeated requests
- **CAPTCHA challenges**: These cannot be bypassed automatically
- **Dynamic content**: Some content loads via JavaScript

For production use, consider:
- Using rotating proxies
- Implementing more sophisticated headers
- Respecting robots.txt files
- Obtaining permission from the platforms when possible

## Demo Mode vs Live Scraping

**Demo Mode** (recommended for testing):
- Generates realistic sample data
- No rate limits or blocking issues
- Fast execution
- Consistent results

**Live Scraping** (for real data):
- May encounter 403/429 errors
- Slower due to rate limiting
- Results depend on platform availability
- May require additional configuration

## Error Handling

The script includes comprehensive error handling for:
- Invalid input parameters
- Network connectivity issues
- HTTP errors (404, 403, 500, etc.)
- Missing or malformed review data
- Date parsing errors

All errors are logged to `review_scraper.log` for debugging purposes.

## Project Structure

```
saas-review-scraper/
├── review_scraper.py          # Main CLI script
├── g2_scraper.py             # G2 scraper implementation
├── capterra_scraper.py       # Capterra scraper implementation
├── software_advice_scraper.py # Software Advice scraper implementation
├── utils.py                  # Utility functions
├── config.py                 # Configuration settings
├── test_scraper.py           # Test script
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── output/                  # Output directory for JSON files
```

## Testing

Run the test script to verify the installation and generate sample data:

```bash
python test_scraper.py
```

This will:
1. Test date validation functions
2. Generate sample review data
3. Verify JSON output format
4. Check all dependencies

## Contributing

To extend this script:
1. Add new scrapers by following the existing pattern
2. Update the `SOURCES` list in the main script
3. Add new platforms to the CLI options
4. Test thoroughly with demo mode first

## Legal and Ethical Considerations

- Always respect website terms of service
- Use reasonable delays between requests
- Consider obtaining explicit permission for large-scale scraping
- Be mindful of rate limits and server load
- Use the data responsibly and in compliance with applicable laws

## Support

For issues or questions:
1. Check the log file (`review_scraper.log`) for error details
2. Use demo mode to test functionality
3. Verify your date formats and company names
4. Check network connectivity and firewall settings