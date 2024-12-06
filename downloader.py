import aiohttp
import asyncio
from tqdm.asyncio import tqdm
import json
import os
import time
from pathlib import Path
import humanize
from datetime import datetime

class BatchDownloader:
    def __init__(self, json_file, batch_size=3):
        self.json_file = json_file
        self.batch_size = batch_size
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        self.progress_file = self.download_dir / "download_progress.json"
        self.semaphore = asyncio.Semaphore(batch_size)
        
    def load_links(self):
        with open(self.json_file) as f:
            return json.load(f)
            
    def load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return set(json.load(f))
        return set()

    def save_progress(self, url):
        progress = self.load_progress()
        progress.add(url)
        with open(self.progress_file, 'w') as f:
            json.dump(list(progress), f)

    async def download_file(self, link_data):
        initial_url = link_data['initial_url']
        download_url = link_data['final_url']
        
        # Extract filename from initial URL
        filename = initial_url.split('#')[1]
        filepath = self.download_dir / filename
        
        if filepath.exists():
            print(f"\nSkipping {filename} - already exists")
            return
            
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(download_url) as response:
                        if response.status != 200:
                            print(f"\nError downloading {filename}: {response.status}")
                            return
                            
                        total_size = int(response.headers.get('content-length', 0))
                        
                        with tqdm(
                            total=total_size,
                            unit='iB',
                            unit_scale=True,
                            unit_divisor=1024,
                            desc=filename,
                            leave=True
                        ) as progress_bar:
                            
                            with open(filepath, 'wb') as f:
                                start_time = time.time()
                                downloaded = 0
                                
                                async for chunk in response.content.iter_chunked(8192):
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    progress_bar.update(len(chunk))
                                    
                                    # Calculate speed
                                    elapsed = time.time() - start_time
                                    if elapsed > 0:
                                        speed = downloaded / elapsed
                                        progress_bar.set_postfix({
                                            'speed': f'{humanize.naturalsize(speed)}/s'
                                        })
                
                self.save_progress(initial_url)
                
            except Exception as e:
                print(f"\nError downloading {filename}: {str(e)}")
                if filepath.exists():
                    filepath.unlink()

    async def download_all(self):
        links = self.load_links()
        completed = self.load_progress()
        remaining = [link for link in links if link['initial_url'] not in completed]
        
        if not remaining:
            print("All downloads completed!")
            return
            
        print(f"Starting downloads: {len(remaining)} files remaining")
        await asyncio.gather(*[self.download_file(link) for link in remaining])

def main():
    downloader = BatchDownloader('final_download_links.json', batch_size=3)
    asyncio.run(downloader.download_all())

if __name__ == "__main__":
    main()