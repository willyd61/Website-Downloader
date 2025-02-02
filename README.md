# Website Downloader

A Python script that downloads complete websites while preserving their structure and assets.

## Features

✅ Downloads and organizes:
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


## License

MIT License - Feel free to use and modify
