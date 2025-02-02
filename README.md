# Website Downloader

A Python script that downloads complete websites while preserving their structure and assets.

## ⚠️ Disclaimer

This tool is provided for educational and personal use only. Before downloading any website content:

1. **Legal Considerations:**
   - Ensure you have the right to download and use the content
   - Respect website terms of service and robots.txt rules
   - Be aware of copyright and intellectual property rights

2. **Usage Guidelines:**
   - Do not use for unauthorized data collection
   - Respect website bandwidth and server resources
   - Follow website crawling policies and rate limits

3. **Limitations:**
   - This tool may not work with all websites
   - Some websites may block automated downloads
   - Dynamic content might not be captured completely

The developer(s) of this tool are not responsible for:
- Any misuse of the downloaded content
- Damage to any computer systems or networks
- Legal consequences of unauthorized use

## Features

- HTML pages with proper structure
- CSS stylesheets with resolved dependencies
- Font files in various formats
- SVG graphics with correct encoding
- Images (PNG, JPG, WebP, etc.)
- JavaScript files and other resources

## Prerequisites

Ensure you have Python 3.x installed and install the required packages:

`pip install selenium requests cssutils urllib3`


# Usage

Run the script:
`python main.py`

When prompted:
- Enter the website URL (e.g., https://example.com)
- Specify output directory name (e.g., downloads)

The script will create the specified directory and download all website content while maintaining the original structure.

## Example

- Enter website URL: https://example.com
- Enter output directory: example_site

