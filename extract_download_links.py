from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
import os
import time
from webdriver_manager.microsoft import EdgeChromiumDriverManager

class DownloadLinkExtractor:
    def __init__(self):
        self.output_file = "final_download_links.json"
        self.setup_browser()

    def setup_browser(self):
        options = Options()
        options.add_argument('--headless')  # Run in background
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=options)

    def get_initial_links(self, url):
        print("Fetching initial links...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return [a['href'] for a in soup.find_all('a', href=True) 
                if "fuckingfast.co" in a['href']]

    def get_final_download_link(self, url):
        try:
            self.driver.get(url)
            
            # Get page source and extract download link using regex
            import re
            page_source = self.driver.page_source
            # Use raw string (r prefix) for regex pattern
            download_pattern = r'window\.open\("(https://fuckingfast\.co/dl/[^"]+)"\)'
            match = re.search(download_pattern, page_source)
            
            if match:
                final_url = match.group(1)
                return {
                    'initial_url': url,
                    'final_url': final_url,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # Use raw string for JavaScript code
                script = r"""
                let downloadFunc = document.querySelector('.link-button').getAttribute('onclick');
                if (downloadFunc) {
                    return downloadFunc.toString().match(/window\.open\("([^"]+)"\)/)[1];
                }
                return null;
                """
                final_url = self.driver.execute_script(script)
                
                if final_url:
                    return {
                        'initial_url': url,
                        'final_url': final_url,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                
            print(f"Could not extract download link from {url}")
            return None
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None
        finally:
            # Clear any extra tabs
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def save_links(self, links):
        with open(self.output_file, 'w') as f:
            json.dump(links, f, indent=2)
        print(f"Links saved to {self.output_file}")

    def extract_all_links(self, fitgirl_url):
        initial_links = self.get_initial_links(fitgirl_url)
        print(f"Found {len(initial_links)} initial links")
        
        final_links = []
        for i, link in enumerate(initial_links, 1):
            print(f"\nProcessing link {i}/{len(initial_links)}")
            final_link = self.get_final_download_link(link)
            if final_link:
                final_links.append(final_link)
        
        self.save_links(final_links)
        return final_links

    def cleanup(self):
        self.driver.quit()

def main():
    url = input("Enter Fitgirl Repack page URL: ").strip()
    if not url:
        print("Please provide a valid URL")
        return

    extractor = DownloadLinkExtractor()
    try:
        extractor.extract_all_links(url)
    finally:
        extractor.cleanup()

if __name__ == "__main__":
    main()