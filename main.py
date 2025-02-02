from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, time, requests, re, cssutils, logging, urllib3
from urllib.parse import urljoin, urlparse

cssutils.log.setLevel(logging.CRITICAL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebsiteDownloader:
    def __init__(self, url, output_dir):
        self.base_url = url if url.startswith(('http://', 'https://')) else 'https://' + url
        self.output_dir = os.path.abspath(output_dir)
        self.downloaded_files = set()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'identity'  # Changed to prevent compression
        }
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        os.makedirs(self.output_dir, exist_ok=True)

    def verify_and_fix_svg(self, content):
        if not content.strip().startswith(('<svg', '<?xml')):
            svg_match = re.search(r'<svg[^>]*>.*?</svg>', content, re.DOTALL | re.IGNORECASE)
            if svg_match:
                return svg_match.group(0)
            else:
                raise ValueError("Invalid SVG content")
        return content

    def download_svg(self, url, local_path):
        if url in self.downloaded_files: return
        try:
            print(f"\nDownloading SVG: {url}")
            svg_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                'Accept': 'image/svg+xml,*/*;q=0.8',
                'Accept-Encoding': 'identity',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Origin': self.base_url,
                'Referer': self.base_url
            }

            absolute_url = url if url.startswith(('http://', 'https://')) else urljoin(self.base_url, url)
            response = self.session.get(absolute_url, headers=svg_headers, timeout=15, verify=False)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            content = response.text
            content = self.verify_and_fix_svg(content)

            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            self.downloaded_files.add(url)
            print(f"Saved SVG to: {local_path}")
            
        except Exception as e:
            print(f"Error downloading SVG {url}: {str(e)}")
            try:
                print("Attempting fallback download...")
                response = requests.get(url, headers={'Accept': '*/*', 'Accept-Encoding': 'identity'}, verify=False)
                response.encoding = 'utf-8'
                content = response.text
                if '<svg' in content:
                    with open(local_path, 'w', encoding='utf-8', newline='') as f:
                        f.write(content)
                    print("Fallback download successful")
            except Exception as e2:
                print(f"Fallback download failed: {str(e2)}")

    def download_file(self, url, local_path):
        if url in self.downloaded_files: return
        try:
            print(f"\nDownloading: {url}")
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            if url.endswith('.svg'):
                response.encoding = 'utf-8'
                with open(local_path, 'w', encoding='utf-8', newline='') as f:
                    f.write(response.text)
            else:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                    
            self.downloaded_files.add(url)
            print(f"Saved to: {local_path}")
            if local_path.endswith('.css'): self.process_css_urls(response.text, url)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")

    def process_css_urls(self, css_content, css_url):
        try:
            urls = re.findall(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', css_content)
            for url in urls:
                try:
                    if url.startswith('data:'): continue
                    if 'backgroundPattern.svg' in url:
                        absolute_url = urljoin(self.base_url, 'assets/backgroundPattern.svg')
                    else:
                        absolute_url = urljoin(css_url, url)
                    if self.is_same_domain(absolute_url) or url.startswith('/'):
                        local_path = os.path.join(self.output_dir, urlparse(absolute_url).path.lstrip('/'))
                        if url.endswith('.svg'): self.download_svg(absolute_url, local_path)
                        else: self.download_file(absolute_url, local_path)
                except Exception as e:
                    print(f"Error processing URL {url} in CSS: {str(e)}")
        except Exception as e:
            print(f"Error processing CSS URLs from {css_url}: {str(e)}")

    def is_same_domain(self, url):
        try: return urlparse(url).netloc == urlparse(self.base_url).netloc
        except: return False

    def save_page(self, driver, url, local_path):
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"Saved page: {url} to {local_path}")
            resources = {
                'img': ['src', 'data-src'],
                'link': ['href'],
                'script': ['src'],
                'source': ['src'],
                'video': ['src', 'poster'],
                'audio': ['src'],
                'object': ['data'],
                'embed': ['src'],
                'svg': ['data', 'href']
            }
            for tag, attrs in resources.items():
                for element in driver.find_elements(By.TAG_NAME, tag):
                    for attr in attrs:
                        try:
                            resource_url = element.get_attribute(attr)
                            if resource_url and not resource_url.startswith(('data:', '#')):
                                absolute_url = urljoin(url, resource_url)
                                if self.is_same_domain(absolute_url):
                                    local_path = os.path.join(self.output_dir, urlparse(absolute_url).path.lstrip('/'))
                                    if resource_url.endswith('.svg'): self.download_svg(absolute_url, local_path)
                                    else: self.download_file(absolute_url, local_path)
                        except: continue
        except Exception as e:
            print(f"Error saving page {url}: {str(e)}")

    def download_website(self):
        driver = None
        try:
            print(f"\nStarting download of {self.base_url}")
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(self.base_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.save_page(driver, self.base_url, os.path.join(self.output_dir, 'index.html'))
            internal_links = {link.get_attribute('href') for link in driver.find_elements(By.TAG_NAME, 'a')
                            if link.get_attribute('href') and self.is_same_domain(link.get_attribute('href'))}
            for link in internal_links:
                try:
                    driver.get(link)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    local_path = os.path.join(self.output_dir, urlparse(link).path.lstrip('/') or 'index.html')
                    if not local_path.endswith('.html'): local_path = os.path.join(local_path, 'index.html')
                    self.save_page(driver, link, local_path)
                    time.sleep(1)
                except Exception as e:
                    print(f"Error processing link {link}: {str(e)}")
        finally:
            if driver: driver.quit()

def main():
    try:
        url = input("Enter website URL: ").strip()
        if not url: raise ValueError("URL cannot be empty")
        output_dir = input("Enter output directory: ").strip()
        if not output_dir: raise ValueError("Output directory cannot be empty")
        downloader = WebsiteDownloader(url, output_dir)
        downloader.download_website()
        print("\nWebsite download completed!")
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
