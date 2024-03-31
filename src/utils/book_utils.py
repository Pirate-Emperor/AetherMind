import requests
import streamlit as st
import os
import re
from urllib.parse import quote
import unicodedata
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


IMAGE_CACHE_BASE = 'static/image_cache'

def get_book_cover_from_douban(title):
    encoded_title = quote(title)
    url = f"https://book.douban.com/j/subject_suggest?q={encoded_title}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    print(f'Getting book cover from Douban... {url}', flush=True)
    response = requests.get(url, headers=headers)
    print(response.text, response.status_code, flush=True)
    if response.status_code == 200:
        try:
            results = response.json()
            print(results, flush=True)
            if results:
                pic_url = results[0].get('pic')
                # if pic_url:
                #     pic_url = pic_url.replace('/s/', '/m/')
                return pic_url
        except Exception as e:
            print(e, flush=True)
            return None
    return None

def upload_image_to_imgur(file, title, description):
    print('Uploading image to Imgur...')
    url = "https://api.imgur.com/3/image"
    headers = {
        "Authorization": f"Client-ID {st.secrets['imgur']['client_id']}"
    }
    data = {
        "image": file,
        "type": "file",
        "title": title,
        "description": description
    }
    response = requests.post(url, headers=headers, files=data)
    if response.status_code == 200:
        try:
            result = response.json()
            print(result, flush=True)
            return result['data']['link']
        except Exception as e:
            print(e, flush=True)
            return None
    return None

def get_image_from_url(url):
    # Check if image is already in cache
    cache_path = parse_url_to_cache_path(url)
    if os.path.exists(cache_path):
        # print(f'Image found in cache: {cache_path}', flush=True)
        return cache_path
    print(f'Fetching image bytes from URL... {url}', flush=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        image_bytes = response.content
        if len(image_bytes) == 0:
            print(f"Image empty at {url}", flush=True)
            return None
        # Write image bytes to cache
        cache_path = parse_url_to_cache_path(url)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'wb') as f:
            f.write(image_bytes)
        print(f'Image cached at: {cache_path}', flush=True)
        return cache_path
    else:
        print(f'Failed to fetch image. Status code: {response.status_code}', flush=True)
        return None
    
def parse_url_to_cache_path(url):
    # Remove the protocol (http://, https://, etc.)
    url = re.sub(r'^https?://', '', url)
    
    # Replace special characters with underscores
    url = re.sub(r'[^\w\-_\. ]', '_', url)
    
    # Remove any non-ASCII characters
    url = unicodedata.normalize('NFKD', url).encode('ASCII', 'ignore').decode('ASCII')
    
    # Truncate to a reasonable length (e.g., 255 characters)
    max_length = 255
    if len(url) > max_length:
        url = url[:max_length]
        
    cache_path = os.path.join(IMAGE_CACHE_BASE, url)
    
    return cache_path
    
def parse_epub_to_txt(epub_path):
    ebook = epub.read_epub(epub_path)
    book_content = ""
    
    # Get the title
    title = ebook.get_metadata('DC', 'title')[0][0] if ebook.get_metadata('DC', 'title') else "Unknown Title"
    
    # Get the table of contents
    toc = ebook.toc
    
    # Function to extract text from TOC items
    def extract_toc_text(toc_item):
        if isinstance(toc_item, tuple):
            return toc_item[0]
        elif hasattr(toc_item, 'title'):
            return toc_item.title
        return str(toc_item)
    
    # Function to get the href from TOC items
    def extract_toc_href(toc_item):
        if isinstance(toc_item, tuple) and len(toc_item) > 1:
            return toc_item[1]
        elif hasattr(toc_item, 'href'):
            return toc_item.href
        return None
    
    # Function to process TOC items and their content
    def process_toc_item(item, is_first_item=False, level=0):
        nonlocal book_content
        title = extract_toc_text(item)
        href = extract_toc_href(item)
        
        # Add empty lines before title based on level
        book_content += ("\n" * 5 + title) if not is_first_item else title
        # book_content += "\n" * (5 if level == 0 else 3)
        # book_content += "#" * (level + 1) + f" {title}\n\n"
        
        if href and href in href_content_map:
            book_content += "\n" * 3 + href_content_map[href]
            # paragraphs = href_content_map[href].split('\n')
            # for paragraph in paragraphs:
            #     # if paragraph.strip():
            #     book_content += paragraph.strip() + "\n\n"
        
        # Process sub-items if any
        if isinstance(item, tuple) and len(item) > 1 and isinstance(item[1], list):
            for subitem in item[1]:
                process_toc_item(subitem, level + 1)
    
    # Create a dictionary to map hrefs to their content
    href_content_map = {}
    
    # Get all items in reading order
    spine_items = ebook.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    
    for item in spine_items:
        # Extract content from each item
        content = item.get_content().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract and clean text content
        divs = soup.find_all('div')
        text = '\n\n'.join([div.get_text(strip=True) for div in divs])
        href_content_map[item.get_name()] = text
    
    # Count the number of notes
    note_count = sum(len(href_content_map[extract_toc_href(item)].split('\n\n')) for item in toc if extract_toc_href(item) in href_content_map)
    
    # Build the content
    book_content += f"{title}\n\n\n{note_count}个笔记\n\n"
    
    # Process the TOC to order the content
    for idx, item in enumerate(toc):
        title = extract_toc_text(item)
        href = extract_toc_href(item)
        
        if idx > 0:
            book_content += "\n\n"
        if not title:
            title = '正文'
        book_content += title + "\n"
        
        if href and href in href_content_map:
            paragraphs = href_content_map[href].split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    book_content += f"\n◆ {paragraph}\n"
    
    return book_content