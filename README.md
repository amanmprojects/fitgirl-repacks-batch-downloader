# Fitgirl Repacks Batch Downloader

A Python script to automate downloading multiple parts from Fitgirl Repacks using Selenium WebDriver.

## Why This Exists

When downloading large games from Fitgirl Repacks that are split into multiple parts (sometimes 100+ parts), it becomes extremely tedious to manually:

1. Click each download link
2. Wait for the download page to load 
3. Click the download button
4. Repeat for every single part

This script automates this process by handling multiple downloads in batches.

## Features

- Supports both Edge and Chrome browsers
- Downloads files in configurable batch sizes
- Tracks download progress and resumes from last successful download
- Configurable download directory
- Command line interface with multiple options

## Prerequisites

```
pip install -r requirements.txt
```

The script requires:
- Python 3.6+
- Selenium WebDriver
- Edge or Chrome browser installed

## Usage

Basic usage:
```bash
python script.py <url> 
```

Full options:
```bash
python script.py <url> [--browser edge|chrome] [--concurrent N] [--download-dir DIR] [--batch-size N]
```

Arguments:
- 

url

: URL of the Fitgirl Repacks page containing download links
- `--browser`: Browser to use for downloads (default: edge)
- `--concurrent`: Number of concurrent downloads (default: 1) 
- `--download-dir`: Download directory (default: ./downloaded_files)
- `--batch-size`: Number of files to process in each batch (default: 5)

Example:
```bash
python script.py https://fitgirl-repacks.site/game-name --browser chrome --download-dir D:\Downloads --batch-size 10
```

## Important Note

This tool is for educational purposes only. Users should consider bandwidth limitations and website terms of service. Whether to use this tool as well as [Fitgirl Repacks](https://fitgirl-repacks.site) is up to individual discretion and responsibility.

## License

MIT License
