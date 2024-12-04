from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import argparse
import os
import time
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager

def setup_args():
    parser = argparse.ArgumentParser(description='Download files from FuckingFast links')
    parser.add_argument('url', help='URL of the page containing download links')
    parser.add_argument('--browser', choices=['edge', 'chrome'], default='edge',
                      help='Browser to use (default: edge)')
    parser.add_argument('--concurrent', type=int, default=1,
                      help='Number of concurrent downloads (default: 1, might not work due to server limitations)')
    parser.add_argument('--download-dir', default='./downloaded_files',
                      help='Download directory (default: ./downloaded_files)')
    parser.add_argument('--batch-size', type=int, default=5,
                      help='Number of files to process in each batch (default: 5)')
    return parser.parse_args()

def setup_browser(browser_type, download_dir):
    """Setup and return webdriver based on user choice"""
    if browser_type == 'edge':
        options = EdgeOptions()
        prefs = {"download.default_directory": os.path.abspath(download_dir)}
        options.add_experimental_option("prefs", prefs)
        driver_path = EdgeChromiumDriverManager().install()
        driver = webdriver.Edge(service=EdgeService(driver_path), options=options)
        # Open new window
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        return driver
    else:
        options = ChromeOptions()
        prefs = {"download.default_directory": os.path.abspath(download_dir)}
        options.add_experimental_option("prefs", prefs)
        driver_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)
        # Open new window
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        return driver

def extract_links(url):
    """Extract download links from the given URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a['href'] for a in soup.find_all('a', href=True) if "fuckingfast.co" in a['href']]
        print(f"Number of download links found: {len(links)}")
        return links
    except Exception as e:
        print(f"Error extracting links: {e}")
        exit(1)

def process_download(driver, url, progress_file):
    """Process a single download"""
    try:
        driver.get(url)
        
        # Find and click download button
        download_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "link-button"))
        )
        
        # First click (opens ad)
        download_button.click()
        
        # Handle ad in new tab
        ad_handle = driver.window_handles[-1]
        driver.switch_to.window(ad_handle)
        driver.close()
        
        # Switch back to download window
        driver.switch_to.window(driver.window_handles[-1])
        
        # Second click (starts download)
        download_button.click()
        
        # Record successful download initiation
        with open(progress_file, 'a') as f:
            f.write(f"{url}\n")
            
        print(f"Download initiated for: {url}")
        
    except Exception as e:
        print(f"Error processing {url}: {e}")

def process_downloads(links, args):
    """Process downloads in batches"""
    # Create download directory if it doesn't exist
    os.makedirs(args.download_dir, exist_ok=True)
    
    progress_file = os.path.join(args.download_dir, "download_progress.txt")
    completed_urls = set()
    
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            completed_urls = set(f.read().splitlines())
    
    remaining_links = [url for url in links if url not in completed_urls]
    
    if not remaining_links:
        print("No new links to process")
        return
        
    print(f"\nProcessing {len(remaining_links)} links...")
    print(f"Downloads will be saved to: {os.path.abspath(args.download_dir)}")
    
    while remaining_links:
        batch = remaining_links[:args.batch_size]
        remaining_links = remaining_links[args.batch_size:]
        
        drivers = [setup_browser(args.browser, args.download_dir) 
                  for _ in range(min(args.concurrent, len(batch)))]
        
        try:
            for i, url in enumerate(batch):
                driver_index = i % len(drivers)
                process_download(drivers[driver_index], url, progress_file)
                time.sleep(2)  # Small delay between downloads
                
            # Wait for downloads to complete
            time.sleep(30)
            
        except Exception as e:
            print(f"Error in batch: {e}")
        finally:
            for driver in drivers:
                driver.quit()
        
        print(f"Batch completed. Waiting before next batch...")
        time.sleep(10)

def main():
    args = setup_args()
    links = extract_links(args.url)
    
    if not links:
        print("No links found. Exiting...")
        return
        
    if input("Do you want to proceed? (y/n): ").lower() != 'y':
        print("Exiting...")
        return
        
    process_downloads(links, args)

if __name__ == "__main__":
    main()
