import requests
from bs4 import BeautifulSoup
import time
import os
from java import jclass

Log = jclass("android.util.Log")
stop_flag = False

def extract_chapter_content(soup, chapter_link, stdout_callback):
    content_div = soup.find('div', id='chr-content')
    if not content_div:
        stdout_callback('Chapter content not found!')
        return None, None

    content_tag = content_div.find('p').find_next_sibling()

    content = []
    while content_tag and content_tag.name != 'div':
        if content_tag.name == 'p':
            content.append(content_tag.get_text(strip=True).replace('“', "\"").replace('”', "\"").replace('’', "\'"))
        content_tag = content_tag.find_next_sibling()
    
    a_tag = soup.find('a', href=chapter_link)
    if not a_tag:
        stdout_callback('Chapter heading not found!')
        return None, None
    chapter_heading = a_tag.get('title')

    return chapter_heading, "\n".join(content)

def curling(chapter_number, base_url, chapter_link, folder_name, webnovel_link, stdout_callback):
    fail_safe = 0
    Log.i("MyTag", f'{chapter_link}')
    global stop_flag
    stop_flag = False
    
    while chapter_link != "" and fail_safe < 100 and not stop_flag:
        time.sleep(2)
        fail_safe += 1
        url = base_url + chapter_link
        Log.i("MyTag", f'{url}')
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        chapter_heading, extracted_text = extract_chapter_content(soup, chapter_link, stdout_callback)
        Log.i("MyTag", f'{chapter_heading}')
        if not chapter_heading or not extracted_text:
            stdout_callback("Error extracting chapter content")
            return
        

        link_tag = soup.find('a', id='next_chap')
        if link_tag:
            chapter_link = link_tag.get('href')
            if not chapter_link:
                base_url = webnovel_link
                chapter_link = ""
        else:
            stdout_callback("Next chapter link not found")
            return
        
        stdout_callback(f"Downloaded: {chapter_heading}")

        with open(os.path.join(folder_name, f'{chapter_number}'), 'w', encoding='utf-8') as file:
            file.write(chapter_heading + "\n")
            file.write(extracted_text)
        with open(os.path.join(folder_name, 'final'), 'w') as f:
            f.write(str(chapter_number) + '||' + url)     
        with open(os.path.join(folder_name, 'index'), 'a') as f:
            f.write(chapter_heading + "\n")   
        chapter_number += 1

def downloadChapters(webnovel_link, stdout_callback, writable_directory):
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
                stdout_callback("Next chapter link not found")
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
            stdout_callback("Chapter 1 link not found!!")
            return

        start = 1

    curling(start, base_url, chapter_link, folder_path, webnovel_link, stdout_callback)

def stopDownload():
    global stop_flag
    stop_flag = True