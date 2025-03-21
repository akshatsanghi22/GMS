import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import time
import sys
import io
from datetime import datetime
import os
from gms_multi import GoogleMapsScraper, logger

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        pass

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Maps Scraper")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.scraper = None
        self.scraping_thread = None
        self.timer_thread = None
        self.is_scraping = False
        self.start_time = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Scraping Configuration", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Queries input
        ttk.Label(input_frame, text="Search Queries (one per line):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.queries_text = scrolledtext.ScrolledText(input_frame, width=40, height=5)
        self.queries_text.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Max listings input
        ttk.Label(input_frame, text="Max Listings per Query:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_listings_var = tk.StringVar(value="5")
        self.max_listings_entry = ttk.Spinbox(input_frame, from_=1, to=20, textvariable=self.max_listings_var, width=10)
        self.max_listings_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Output file selection
        ttk.Label(input_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar(value="google_maps_results.csv")
        output_frame = ttk.Frame(input_frame)
        output_frame.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file_var, width=30)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_btn = ttk.Button(output_frame, text="Browse", command=self.browse_output_file)
        self.browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # Headless mode checkbox
        self.headless_var = tk.BooleanVar(value=True)
        self.headless_check = ttk.Checkbutton(input_frame, text="Headless Mode", variable=self.headless_var)
        self.headless_check.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Threads input
        ttk.Label(input_frame, text="Number of Threads:").grid(row=3, column=1, sticky=tk.W, pady=5)
        self.threads_var = tk.StringVar(value="1")
        self.threads_entry = ttk.Spinbox(input_frame, from_=1, to=8, textvariable=self.threads_var, width=10)
        self.threads_entry.grid(row=3, column=1, sticky=tk.E, pady=5)
        
        # Timer display
        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.timer_label = ttk.Label(timer_frame, text="Elapsed Time: 00:00:00", font=("Arial", 12))
        self.timer_label.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(timer_frame, text="Status: Ready", font=("Arial", 12))
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Control buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(buttons_frame, text="Start Scraping", command=self.start_scraping)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="Stop Scraping", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Redirect stdout to our log text widget
        self.stdout_redirect = RedirectText(self.log_text)
        sys.stdout = self.stdout_redirect
        
        # Configure input_frame columns
        input_frame.columnconfigure(1, weight=1)
        
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
    
    def update_timer(self):
        while self.is_scraping:
            elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"Elapsed Time: {hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            time.sleep(1)
    
    def start_scraping(self):
        # Get input values
        queries_text = self.queries_text.get("1.0", tk.END).strip()
        if not queries_text:
            self.log_message("Error: No queries provided!")
            return
        
        queries = [q.strip() for q in queries_text.split("\n") if q.strip()]
        
        try:
            max_listings = int(self.max_listings_var.get())
        except ValueError:
            self.log_message("Error: Invalid value for Max Listings!")
            return
        
        try:
            threads = int(self.threads_var.get())
        except ValueError:
            self.log_message("Error: Invalid value for Threads!")
            return
        
        output_file = self.output_file_var.get()
        if not output_file:
            self.log_message("Error: No output file specified!")
            return
        
        headless = self.headless_var.get()
        
        # Update UI
        self.is_scraping = True
        self.start_time = time.time()
        self.progress_bar.start(10)
        self.status_label.config(text="Status: Scraping...")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        # Start scraping thread
        self.scraping_thread = threading.Thread(
            target=self.run_scraper,
            args=(queries, output_file, max_listings, headless, threads)
        )
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
    
    def run_scraper(self, queries, output_file, max_listings, headless, threads):
        try:
            # Initialize the scraper
            self.log_message(f"Initializing scraper with {threads} thread(s), headless mode: {headless}")
            self.scraper = GoogleMapsScraper(headless=headless, num_threads=threads)
            
            # Define fields to extract
            fields = [
                'Name', 'Street', 'City', 'State', 'Zip', 'Country',
                'Phone', 'Website', 'Rating', 'Reviews', 'Category',
                'Status', 'Description', 'Services', 'Image_URL',
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ]
            
            # Start scraping
            self.log_message(f"Starting scraping {len(queries)} queries with up to {max_listings} listings per query")
            success = self.scraper.scrape_to_csv(queries, output_file, max_listings, fields)
            
            if success:
                self.log_message(f"Scraping completed successfully. Results saved to {output_file}")
            else:
                self.log_message("Scraping completed with errors. Check the logs for details.")
        
        except Exception as e:
            self.log_message(f"Error during scraping: {str(e)}")
        
        finally:
            # Reset UI
            self.root.after(0, self.finish_scraping)
    
    def stop_scraping(self):
        if self.is_scraping:
            self.log_message("Stopping scraping process...")
            self.is_scraping = False
            
            # Wait for threads to complete
            if self.scraping_thread:
                self.scraping_thread.join(1.0)
            
            # Reset UI
            self.finish_scraping()
    
    def finish_scraping(self):
        self.is_scraping = False
        self.progress_bar.stop()
        self.status_label.config(text="Status: Ready")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()