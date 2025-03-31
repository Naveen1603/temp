import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fpdf import FPDF
import time
from concurrent.futures import ThreadPoolExecutor
import re

class WebDocExtractor:
    def __init__(self, start_url, output_dir="extracted_docs", max_pages=50, depth_limit=3):
        """
        Initialize the web document extractor
        
        Args:
            start_url (str): The URL to start extraction from
            output_dir (str): Directory to save PDFs and metadata
            max_pages (int): Maximum number of pages to extract
            depth_limit (int): Maximum recursion depth
        """
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.depth_limit = depth_limit
        self.visited_urls = set()
        self.extracted_docs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def is_valid_url(self, url):
        """Check if URL is valid and belongs to same domain"""
        if not url or not url.startswith('http'):
            return False
        
        # Check if URL belongs to same domain to avoid crawling external sites
        parsed_url = urlparse(url)
        return self.base_domain == parsed_url.netloc
    
    def extract_text_from_html(self, html_content):
        """Extract clean text from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # Get text from paragraphs and headers (better structure)
        content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        
        # Get the title
        title = soup.title.string if soup.title else "Untitled"
        
        # Join all text with proper spacing
        content = [title + "\n\n"]
        for element in content_elements:
            text = element.get_text().strip()
            if text:
                tag_name = element.name
                if tag_name.startswith('h'):
                    # Add spacing for headers to improve readability
                    content.append("\n" + text + "\n")
                else:
                    content.append(text)
        
        return "\n".join(content)
    
    def clean_filename(self, text):
        """Create a valid filename from text"""
        # Replace invalid filename characters
        filename = re.sub(r'[\\/*?:"<>|]', "", text)
        # Limit length and remove extra whitespace
        return filename[:50].strip().replace(" ", "_")
    
    def create_pdf(self, title, content, filename):
        """Convert text content to PDF with good formatting"""
        pdf = FPDF()
        pdf.add_page()
        
        # Set PDF metadata
        pdf.set_title(title)
        
        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, 0, 1, "C")
        pdf.ln(10)
        
        # Add content
        pdf.set_font("Arial", "", 12)
        
        # Split content by paragraphs for better formatting
        paragraphs = content.split("\n")
        for paragraph in paragraphs:
            if paragraph.strip():
                # Check if this looks like a heading (shorter text)
                if len(paragraph) < 50 and paragraph.isupper() or paragraph.endswith(':'):
                    pdf.set_font("Arial", "B", 14)
                    pdf.ln(5)
                    pdf.multi_cell(0, 10, paragraph)
                    pdf.set_font("Arial", "", 12)
                    pdf.ln(5)
                else:
                    pdf.multi_cell(0, 10, paragraph)
                    pdf.ln(5)
        
        # Save PDF
        full_path = os.path.join(self.output_dir, filename)
        pdf.output(full_path)
        return full_path
    
    def crawl_url(self, url, depth=0):
        """Crawl a URL and extract document content"""
        # Check if we've reached limits
        if url in self.visited_urls or len(self.extracted_docs) >= self.max_pages or depth > self.depth_limit:
            return
        
        print(f"Crawling: {url} (depth: {depth})")
        self.visited_urls.add(url)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Untitled"
            
            # Extract text content
            content = self.extract_text_from_html(response.text)
            
            # Generate filename
            filename = self.clean_filename(title) + ".pdf"
            
            # Create PDF
            pdf_path = self.create_pdf(title, content, filename)
            
            # Add to extracted documents
            self.extracted_docs.append({
                'title': title,
                'url': url,
                'filename': filename,
                'path': pdf_path
            })
            
            # Find links for recursive crawling
            if depth < self.depth_limit and len(self.extracted_docs) < self.max_pages:
                links = soup.find_all('a', href=True)
                new_urls = []
                
                for link in links:
                    href = link['href']
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    
                    if (self.is_valid_url(absolute_url) and 
                        absolute_url not in self.visited_urls and
                        len(self.extracted_docs) < self.max_pages):
                        new_urls.append((absolute_url, depth + 1))
                
                # Process new URLs with thread pool for faster execution
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for new_url, new_depth in new_urls:
                        executor.submit(self.crawl_url, new_url, new_depth)
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
    
    def extract_documents(self):
        """Main method to extract documents from URLs"""
        start_time = time.time()
        
        # Start crawling from the initial URL
        self.crawl_url(self.start_url)
        
        # Create Excel metadata file
        if self.extracted_docs:
            df = pd.DataFrame(self.extracted_docs)
            excel_path = os.path.join(self.output_dir, "document_metadata.xlsx")
            df.to_excel(excel_path, index=False)
            print(f"Metadata saved to: {excel_path}")
        
        elapsed_time = time.time() - start_time
        print(f"Extraction completed. Processed {len(self.visited_urls)} URLs, extracted {len(self.extracted_docs)} documents in {elapsed_time:.2f} seconds")
        return self.extracted_docs

# Example usage
if __name__ == "__main__":
    # Configure parameters
    start_url = "https://example.com/documentation/"  # Replace with your target URL
    output_directory = "extracted_documents"
    max_pages = 100  # Limit to prevent excessive crawling
    max_depth = 3    # How deep to follow links
    
    # Initialize and run the extractor
    extractor = WebDocExtractor(
        start_url=start_url,
        output_dir=output_directory,
        max_pages=max_pages,
        depth_limit=max_depth
    )
    
    # Start extraction
    results = extractor.extract_documents()
    print(f"Extracted {len(results)} documents.")
