import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

output_dir = 'site-results'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

base_url = 'https://thereviewsolution.com'
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to subpages with http or https scheme
links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True) if a['href'].startswith('http')]

print(f'Found {len(links)} links to subpages')

# Extract content from main page and subpages
file_number = 1
for url in [base_url] + links:
    try:
        print(f'Extracting content from {url}')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find the main content of the page
        main_body = soup.find('main') or soup.find('div', {'id': 'main'}) or soup.find('article') or soup.body

        if main_body is not None:
            # Remove unwanted elements
            for tag in main_body.find_all(['header', 'footer', 'aside']):
                tag.decompose()

            for tag in main_body.find_all(['div', 'section']):
                if 'sidebar' in tag.get('class', []) or 'ad' in tag.get('class', []):
                    tag.decompose()

            # Add line breaks for paragraphs
            for p in main_body.find_all('p'):
                p.append('\n\n')

            # Add line breaks and dashes for headings
            for h in main_body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                level = int(h.name[1])
                h.insert_before('\n\n' + '-' * level + ' ')
                h.append('\n\n')

            text = main_body.get_text()

            # Remove extra white space
            text = re.sub(r'\n\s*\n', '\n\n', text)

            filename = os.path.join(output_dir, f'{file_number}.txt')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)

            file_number += 1
        else:
            print(f'Could not find main content on {url}')
    except Exception as e:
        with open(os.path.join(output_dir, 'exceptions.txt'), 'a') as f:
            f.write(f'{url}: {e}\n')
