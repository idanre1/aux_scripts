import requests
from bs4 import BeautifulSoup

def get_xls_links(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    xls_links = [link['href'] for link in links if link['href'].endswith('.xls')]
    return xls_links

import os

def save_links_to_file(url, filename):
    links = get_xls_links(url)
    with open(filename, 'w') as f:
        for link in links:
            f.write(link + '\n')

def download_files(filename):
    with open(filename, 'r') as f:
        links = f.readlines()
    for link in links:
        os.system(f'wget --no-check-certificate {link.strip()}')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Download xls files from a given URL')
    parser.add_argument('url', help='URL to fetch xls links from')
    parser.add_argument('-o', '--output', default='links.txt', help='Output file to save links to')
    args = parser.parse_args()

    save_links_to_file(args.url, args.output)
    # download_files(args.output)
    print(f'wget --no-check-certificate -i {args.output} -w 3')