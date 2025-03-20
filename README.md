# Google Maps Scraper Flask Project

A web application that provides a user-friendly interface for extracting data from Google Maps. This project combines a powerful Google Maps scraper with a Flask web interface, allowing users to extract business information, contact details, reviews, and more from Google Maps.

## Features

- **User-friendly Web Interface**: Easy-to-use interface for configuring and running scraping jobs
- **Multiple Search Queries**: Process multiple search queries in a single job
- **Customizable Data Extraction**: Select which data points to extract (business name, address, phone, website, ratings, reviews)
- **Multiple Export Formats**: Export data in CSV, JSON, or Excel formats
- **Multi-threaded Scraping**: Option to use multiple threads for faster scraping
- **Real-time Progress Tracking**: Monitor the progress of your scraping jobs in real-time
- **Job History**: Keep track of your scraping jobs and their results
- **Responsive Design**: Works on desktop and mobile devices

## Installation

### Prerequisites

- Python 3.7 or higher
- Chrome browser (latest version recommended)
- ChromeDriver (will be automatically downloaded by webdriver-manager)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd google-maps-scraper-flask
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Project Structure

```
google-maps-scraper-flask/
├── app.py                 # Main Flask application
├── multi_gms.py           # Google Maps scraper implementation
├── templates/             # HTML templates
│   ├── index.html         # Home page / Scraper interface
│   ├── about.html         # About page
│   ├── service.html       # Services page
│   ├── why.html           # Why Us page
│   ├── team.html          # Team page
│   ├── 404.html           # 404 error page
│   └── 500.html           # 500 error page
├── static/                # Static files
│   ├── css/               # CSS files
│   ├── js/                # JavaScript files
│   ├── images/            # Image files
│   └── fonts/             # Font files
├── downloads/             # Directory for downloaded results
├── debug_screenshots/     # Debugging screenshots (created automatically)
└── requirements.txt       # Python dependencies
```

## Requirements

Create a `requirements.txt` file with the following dependencies:

```
flask==2.2.3
pandas==1.5.3
selenium==4.8.2
beautifulsoup4==4.12.0
webdriver-manager==3.8.5
lxml==4.9.2
requests==2.28.2
openpyxl==3.1.1
```

## Running the Application

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. On the home page, click on "Get Started" or navigate to the scraper section.
2. Enter your search queries (one per line).
3. Configure the scraping parameters:
   - Number of results per query
   - Number of threads
   - Output format (CSV, JSON, Excel)
   - Data points to extract
4. Click "Start Scraping" to begin the data extraction process.
5. Monitor the progress on the Results tab.
6. Once the scraping is complete, download your results file.

## Notes

- **Rate Limiting**: Be mindful of Google's rate limiting. Using too many threads or making too many requests in a short period may result in temporary blocks.
- **Headless Mode**: The scraper operates in headless mode by default (browser runs in the background). You can disable this for debugging.
- **Screenshots**: The scraper automatically saves screenshots in the `debug_screenshots` folder when errors occur, which can help with troubleshooting.

## License

[MIT License](LICENSE)

## Acknowledgements

- This project uses Selenium and BeautifulSoup for web scraping
- The UI is based on a Bootstrap template
- Thanks to the open-source community for providing the tools and libraries that make this project possible
