from flask import Flask, render_template, request, jsonify, url_for, redirect, send_file
import os
import json
import csv
import pandas as pd
from datetime import datetime
import threading
import time
import logging
import io
from werkzeug.utils import secure_filename

# Import your Google Maps scraper
from gms_multi import GoogleMapsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure upload folder for downloaded results
UPLOAD_FOLDER = 'downloads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables to track scraping jobs
scraper_jobs = {}

class ScraperJob:
    def __init__(self, job_id, queries, max_listings, output_format, headless=True, num_threads=1):
        self.job_id = job_id
        self.queries = queries
        self.max_listings = max_listings
        self.output_format = output_format
        self.headless = headless
        self.num_threads = num_threads
        self.status = "initializing"  # initializing, running, completed, failed
        self.progress = 0
        self.start_time = datetime.now()
        self.end_time = None
        self.result_file = None
        self.error_message = None
        self.scraper = None
        self.thread = None
    
    def start(self):
        self.status = "running"
        self.thread = threading.Thread(target=self.run_scraper)
        self.thread.daemon = True
        self.thread.start()
    
    def run_scraper(self):
        try:
            # Create output filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_base = f"gmaps_results_{timestamp}"
            
            if self.output_format == 'csv':
                output_file = os.path.join(UPLOAD_FOLDER, f"{filename_base}.csv")
            elif self.output_format == 'json':
                output_file = os.path.join(UPLOAD_FOLDER, f"{filename_base}.json")
            elif self.output_format == 'excel':
                output_file = os.path.join(UPLOAD_FOLDER, f"{filename_base}.xlsx")
            else:
                output_file = os.path.join(UPLOAD_FOLDER, f"{filename_base}.csv")
                self.output_format = 'csv'  # Default to CSV
                
            # Initialize the scraper
            self.scraper = GoogleMapsScraper(headless=self.headless, num_threads=self.num_threads)
            
            # Define fields to extract
            fields = [
                'Name', 'Street', 'City', 'State', 'Zip', 'Country',
                'Phone', 'Website', 'Rating', 'Reviews', 'Category',
                'Status', 'Description', 'Services', 'Image_URL',
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ]
            
            # Extract data using the scraper
            logger.info(f"Starting scraping job {self.job_id} with {len(self.queries)} queries")
            results_df = self.scraper.scrape_multiple_queries_with_listings(
                self.queries, 
                max_listings_per_query=self.max_listings,
                fields=fields
            )
            
            # Save the results based on the selected format
            if not results_df.empty:
                if self.output_format == 'csv':
                    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
                elif self.output_format == 'json':
                    results_df.to_json(output_file, orient='records', indent=4)
                elif self.output_format == 'excel':
                    results_df.to_excel(output_file, index=False)
                
                self.result_file = os.path.basename(output_file)
                self.status = "completed"
                logger.info(f"Scraping job {self.job_id} completed successfully.")
            else:
                self.status = "failed"
                self.error_message = "No results found for any query."
                logger.warning(f"Scraping job {self.job_id} failed: No results found.")
        
        except Exception as e:
            self.status = "failed"
            self.error_message = str(e)
            logger.error(f"Error in scraping job {self.job_id}: {str(e)}")
        
        finally:
            self.end_time = datetime.now()
            self.progress = 100


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/why')
def why():
    return render_template('why.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    """
    Run the Google Maps scraper with the provided parameters
    """
    try:
        # Get form data
        search_query = request.form.get('search_query', '')
        num_results = int(request.form.get('num_results', 10))
        num_threads = int(request.form.get('num_threads', 1))
        headless = request.form.get('headless', 'true') == 'true'
        
        # Check if multiple queries are provided (separated by newlines)
        queries = [q.strip() for q in search_query.split('\n') if q.strip()]
        
        # Get extraction options
        extract_options = {
            'name': 'extract_name' in request.form,
            'address': 'extract_address' in request.form,
            'phone': 'extract_phone' in request.form,
            'website': 'extract_website' in request.form,
            'rating': 'extract_rating' in request.form,
            'reviews': 'extract_reviews' in request.form
        }
        
        output_format = request.form.get('output_format', 'csv')
        
        # Create a unique job ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(scraper_jobs)+1}"
        
        # Create and start a new scraper job
        job = ScraperJob(
            job_id=job_id,
            queries=queries,
            max_listings=num_results,
            output_format=output_format,
            headless=headless,
            num_threads=num_threads
        )
        
        # Add job to global tracking
        scraper_jobs[job_id] = job
        
        # Start the job
        job.start()
        
        # Return the job ID for status tracking
        return jsonify({
            'status': 'success',
            'message': f'Scraping job started with {len(queries)} queries',
            'job_id': job_id
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error starting scraper: {str(e)}'
        }), 500

@app.route('/check-status/<job_id>', methods=['GET'])
def check_status(job_id):
    """
    Check the status of a running scraper job
    """
    if job_id not in scraper_jobs:
        return jsonify({
            'status': 'error',
            'message': f'Job ID {job_id} not found'
        }), 404
    
    job = scraper_jobs[job_id]
    
    # Calculate elapsed time
    if job.end_time:
        elapsed = (job.end_time - job.start_time).total_seconds()
    else:
        elapsed = (datetime.now() - job.start_time).total_seconds()
    
    # Format elapsed time
    hours, remainder = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    response = {
        'status': job.status,
        'progress': job.progress,
        'elapsed_time': elapsed_formatted,
        'start_time': job.start_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    if job.end_time:
        response['end_time'] = job.end_time.strftime('%Y-%m-%d %H:%M:%S')
    
    if job.error_message:
        response['error'] = job.error_message
    
    if job.result_file:
        response['result_file'] = job.result_file
        response['download_url'] = url_for('download_file', filename=job.result_file)
    
    return jsonify(response)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download the results file
    """
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/cancel-job/<job_id>', methods=['POST'])
def cancel_job(job_id):
    """
    Cancel a running scraper job
    """
    if job_id not in scraper_jobs:
        return jsonify({
            'status': 'error',
            'message': f'Job ID {job_id} not found'
        }), 404
    
    job = scraper_jobs[job_id]
    
    if job.status == "running":
        # Mark the job as cancelled, but we can't easily kill the thread
        job.status = "cancelled"
        job.end_time = datetime.now()
        
        return jsonify({
            'status': 'success',
            'message': f'Job {job_id} has been marked for cancellation'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Job {job_id} is not running (current status: {job.status})'
        }), 400

@app.route('/list-jobs', methods=['GET'])
def list_jobs():
    """
    List all scraper jobs and their statuses
    """
    jobs_list = []
    
    for job_id, job in scraper_jobs.items():
        job_info = {
            'job_id': job_id,
            'status': job.status,
            'start_time': job.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'queries': len(job.queries),
            'max_listings': job.max_listings
        }
        
        if job.end_time:
            job_info['end_time'] = job.end_time.strftime('%Y-%m-%d %H:%M:%S')
            
        if job.result_file:
            job_info['result_file'] = job.result_file
            
        jobs_list.append(job_info)
    
    return jsonify({
        'jobs': jobs_list,
        'total': len(jobs_list)
    })

@app.route('/debug-info', methods=['GET'])
def debug_info():
    """
    Get debug information about the application
    """
    debug_data = {
        'app_version': '1.0.0',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'total_jobs': len(scraper_jobs),
        'active_jobs': sum(1 for job in scraper_jobs.values() if job.status == "running"),
        'completed_jobs': sum(1 for job in scraper_jobs.values() if job.status == "completed"),
        'failed_jobs': sum(1 for job in scraper_jobs.values() if job.status == "failed"),
        'available_result_files': os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []
    }
    
    return jsonify(debug_data)

# Custom error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)