import threading
import requests
from bs4 import BeautifulSoup
import time
import os
from threading import Event

def extract_chapter_content(soup, chapter_link):
    content_div = soup.find('div', id='chr-content')
    if not content_div:
        return None, None

    content_tag = content_div.find('p').find_next_sibling()

    content = []
    while content_tag and content_tag.name != 'div':
        if content_tag.name == 'p':
            content.append(content_tag.get_text(strip=True).replace('“', "\"").replace('”', "\"").replace('’', "\'"))
        content_tag = content_tag.find_next_sibling()
    
    a_tag = soup.find('a', href=chapter_link)
    if not a_tag:
        return None, None
    chapter_heading = a_tag.get('title')

    return chapter_heading, "\n".join(content)

def curling(chapter_number, base_url, chapter_link, folder_name, webnovel_link, stop_Event):
    fail_safe = 0
    
    while chapter_link != "" and fail_safe < 100 and not stop_Event.is_set():
        time.sleep(2)
        fail_safe += 1
        url = base_url + chapter_link
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        chapter_heading, extracted_text = extract_chapter_content(soup, chapter_link)
        if not chapter_heading or not extracted_text:
            return

        link_tag = soup.find('a', id='next_chap')
        if link_tag:
            chapter_link = link_tag.get('href')
            if not chapter_link:
                base_url = webnovel_link
                chapter_link = ""
        else:
            return
        

        with open(os.path.join(folder_name, f'{chapter_number}'), 'w', encoding='utf-8') as file:
            file.write(chapter_heading + "\n")
            file.write(extracted_text)
        with open(os.path.join(folder_name, 'final'), 'w') as f:
            f.write(str(chapter_number) + '||' + url)     
        with open(os.path.join(folder_name, 'index'), 'a') as f:
            f.write(chapter_heading + "\n")   
        chapter_number += 1

def downloadChapters(webnovel_link, writable_directory, stop_Event: threading.Event):
    base_url = 'https://readnovelfull.com'
    folder_name = webnovel_link.split(".")[1].split("/")[-1]
    folder_path = os.path.join(writable_directory, folder_name)
    start = 0
    
    if os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, 'final')):
        with open(os.path.join(folder_path, 'final'), 'r') as f:
            start, chap_link = f.readline().split('||')
            start = int(start) + 1
            response = requests.get(chap_link)
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            link_tag = soup.find('a', id='next_chap')
            if link_tag:
                chapter_link = link_tag.get('href')
                if not chapter_link:
                    return
            else:
                return
    else:
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
        response = requests.get(webnovel_link)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        a_tag = soup.find('a', text="READ NOW")
        if a_tag:
            chapter_link = a_tag.get('href')
        else:
            return

        start = 1

    curling(start, base_url, chapter_link, folder_path, webnovel_link, stop_Event)

def initialise(webnovel_link, writable_directory):
    folder_name = webnovel_link.split(".")[1].split("/")[-1]
    
    folder_path = os.path.join(writable_directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    response = requests.get(webnovel_link)
    html_content = response.content
    chapter_link: str = ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    a_tag = soup.find('a', text="READ NOW")
    if a_tag:
        chapter_link = str(a_tag.get('href'))

        final_file_path = os.path.join(folder_path, 'final')
        index_file_path = os.path.join(folder_path, 'index')
        chapter_1_path = os.path.join(folder_path, '1')
        
        with open(final_file_path, 'w') as final_file:
            final_file.write(f"1||https://readnovelfull.com{chapter_link}")
        
        response1 = requests.get("https://readnovelfull.com" + chapter_link)
        html_content1 = response1.content
        soup1 = BeautifulSoup(html_content1, 'html.parser')
        chapter_heading: str = ""
        extracted_text: str = ""
        chapter_heading, extracted_text = extract_chapter_content(soup1, chapter_link)

        with open(index_file_path, 'w') as index_file:
            index_file.write(f"{chapter_heading}\n")
        with open(chapter_1_path, 'w', encoding='utf-8') as file:
            file.write(chapter_heading + "\n")
            file.write(extracted_text)
    meta_tags = soup.find_all('meta', attrs={"name": "og:image"})
    if meta_tags:
        meta_tag = meta_tags[0]
        image_url = meta_tag.get('content')
        img_response = requests.get(image_url)

        image_path = os.path.join(folder_path, 'image.jpg')
        with open(image_path, 'wb') as image_file:
            image_file.write(img_response.content)