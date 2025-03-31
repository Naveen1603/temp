import os
import time
import logging
import argparse
import pandas as pd
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from concurrent.futures import ThreadPoolExecutor
import re
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("url_scraper.log"),
        logging.StreamHandler()
    ]
)

class URLToPDFScraper:
    def __init__(self, start_url, output_folder="downloaded_pdfs", max_pages=100, delay=1, 
                 max_depth=5, same_domain_only=True, exclude_patterns=None):
        """
        Initialize the URL to PDF scraper.
        
        Args:
            start_url (str): The starting URL to begin scraping from
            output_folder (str): Directory to save PDFs
            max_pages (int): Maximum number of pages to scrape
            delay (float): Delay between requests to avoid overloading servers
            max_depth (int): Maximum depth to follow links
            same_domain_only (bool): Only follow links within the same domain
            exclude_patterns (list): URL patterns to exclude
        """
        self.start_url = start_url
        self.output_folder = output_folder
        self.max_pages = max_pages
        self.delay = delay
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        
        # Default exclude patterns if none provided
        self.exclude_patterns = exclude_patterns or [
            r'\.(jpg|jpeg|png|gif|svg|webp|mp4|mp3|pdf|zip|rar|doc|docx|xls|xlsx)$',
            r'(logout|sign-out|login|sign-in|register|cart|checkout)',
            r'(facebook|twitter|instagram|youtube|linkedin)'
        ]
        
        # Set up variables to track visited URLs
        self.visited_urls = set()
        self.urls_to_visit = []
        self.url_metadata = []
        self.domain = urlparse(start_url).netloc
        
        # Ensure output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # CSS for better PDF rendering
        self.custom_css = CSS(string='''
            @page {
                margin: 1cm;
                size: A4;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
            }
            h1 { font-size: 20pt; margin-top: 20pt; }
            h2 { font-size: 16pt; margin-top: 15pt; }
            p { margin-bottom: 10pt; }
            a { color: blue; text-decoration: none; }
            img { max-width: 100%; height: auto; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f2f2f2; }
        ''')
        
        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()

    def is_valid_url(self, url):
        """Check if a URL should be processed."""
        if not url or not url.startswith('http'):
            return False
        
        # Check if already visited
        if url in self.visited_urls:
            return False
        
        # Check domain constraint
        if self.same_domain_only and urlparse(url).netloc != self.domain:
            return False
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True

    def extract_links(self, url, depth):
        """Extract links from a webpage."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract links
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                
                if self.is_valid_url(full_url):
                    links.append((full_url, depth + 1))
            
            return links, response.text
            
        except (requests.RequestException, Exception) as e:
            logging.error(f"Error extracting links from {url}: {str(e)}")
            return [], None

    def sanitize_filename(self, url):
        """Convert URL to a safe filename."""
        # Extract domain and path
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        
        # Remove any trailing slashes
        if path.endswith('/'):
            path = path[:-1]
        
        # Create a base filename
        if path:
            # Use the last part of the path, or the domain if path is empty
            base_name = os.path.basename(path) or domain
            # Replace any remaining slashes
            base_name = base_name.replace('/', '_')
        else:
            base_name = domain
        
        # Remove any invalid characters
        base_name = re.sub(r'[\\/*?:"<>|]', '', base_name)
        base_name = re.sub(r'\s+', '_', base_name)
        
        # Add a random element to prevent overwriting
        random_suffix = str(random.randint(1000, 9999))
        
        # Ensure the filename is not too long
        if len(base_name) > 50:
            base_name = base_name[:50]
            
        return f"{base_name}_{random_suffix}.pdf"

    def save_to_pdf(self, url, html_content, filename):
        """Save HTML content to PDF."""
        try:
            # Create a temporary file with the HTML content
            html_obj = HTML(string=html_content, base_url=url)
            
            # Generate PDF
            pdf_path = os.path.join(self.output_folder, filename)
            html_obj.write_pdf(pdf_path, 
                              stylesheets=[self.custom_css], 
                              font_config=self.font_config)
            
            file_size = os.path.getsize(pdf_path) / 1024  # Size in KB
            
            logging.info(f"Saved PDF: {filename} - {file_size:.2f} KB")
            return pdf_path
        
        except Exception as e:
            logging.error(f"Error saving PDF for {url}: {str(e)}")
            return None

    def process_url(self, url_data):
        """Process a single URL: extract links and save to PDF."""
        url, depth = url_data
        
        if depth > self.max_depth or url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        logging.info(f"Processing URL: {url} (Depth: {depth})")
        
        # Extract links and HTML content
        links, html_content = self.extract_links(url, depth)
        
        if html_content:
            # Generate a filename for the PDF
            filename = self.sanitize_filename(url)
            
            # Save to PDF
            pdf_path = self.save_to_pdf(url, html_content, filename)
            
            # Add metadata
            self.url_metadata.append({
                'URL': url,
                'Filename': filename,
                'Depth': depth,
                'File Path': pdf_path
            })
        
        # Add a delay to avoid overloading the server
        time.sleep(self.delay)
        
        return links

    def crawl(self):
        """Crawl the website and convert pages to PDFs."""
        logging.info(f"Starting crawl from {self.start_url}")
        logging.info(f"Maximum pages: {self.max_pages}")
        
        # Initialize with the start URL
        self.urls_to_visit.append((self.start_url, 0))
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            while self.urls_to_visit and len(self.visited_urls) < self.max_pages:
                # Get the next URL to process
                current_url_data = self.urls_to_visit.pop(0)
                
                # Process the URL
                new_links = self.process_url(current_url_data)
                
                # Add new links to the queue
                for link in new_links:
                    if link[0] not in self.visited_urls and link[0] not in [url for url, _ in self.urls_to_visit]:
                        self.urls_to_visit.append(link)
                
                logging.info(f"Visited: {len(self.visited_urls)} | Queue: {len(self.urls_to_visit)}")
        
        # Save metadata to Excel
        self.save_metadata()
        
        logging.info(f"Crawl complete. Processed {len(self.visited_urls)} pages.")
        return self.url_metadata

    def save_metadata(self):
        """Save metadata about the PDFs to an Excel file."""
        try:
            df = pd.DataFrame(self.url_metadata)
            excel_path = os.path.join(self.output_folder, "url_metadata.xlsx")
            df.to_excel(excel_path, index=False)
            logging.info(f"Saved metadata to {excel_path}")
        except Exception as e:
            logging.error(f"Error saving metadata: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Convert website pages to PDFs recursively')
    parser.add_argument('url', help='Starting URL to crawl')
    parser.add_argument('--output', '-o', default='downloaded_pdfs', help='Output folder for PDFs')
    parser.add_argument('--max-pages', '-m', type=int, default=100, help='Maximum number of pages to crawl')
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--depth', type=int, default=5, help='Maximum depth to crawl')
    parser.add_argument('--same-domain', action='store_true', help='Only crawl within the same domain')
    
    args = parser.parse_args()
    
    scraper = URLToPDFScraper(
        start_url=args.url,
        output_folder=args.output,
        max_pages=args.max_pages,
        delay=args.delay,
        max_depth=args.depth,
        same_domain_only=args.same_domain
    )
    
    scraper.crawl()

if __name__ == "__main__":
    main()
