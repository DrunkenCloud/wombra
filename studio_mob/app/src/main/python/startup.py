import os
import requests
from bs4 import BeautifulSoup
from java import jclass

Log = jclass("android.util.Log")

def extract_chapter_content(soup, chapter_link):
    Log.d('MyTag', chapter_link)
    content_div = soup.find('div', id='chr-content')
    if not content_div:
        Log.d('MyTag1', chapter_link)
        return None, None

    content_tag = content_div.find('p').find_next_sibling()

    content = []
    while content_tag and content_tag.name != 'div':
        if content_tag.name == 'p':
            content.append(content_tag.get_text(strip=True).replace('“', "\"").replace('”', "\"").replace('’', "\'"))
        content_tag = content_tag.find_next_sibling()
    
    Log.d('MyTag', '\n'.join(content))
    
    a_tag = soup.find('a', href=chapter_link)
    if not a_tag:
        Log.d('MyTag2', chapter_link)
        return None, None
    chapter_heading = a_tag.get('title')

    return chapter_heading, "\n".join(content)

def initialise(webnovel_link, writable_directory):
    folder_name = webnovel_link.split(".")[1].split("/")[-1]
    
    folder_path = os.path.join(writable_directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    response = requests.get(webnovel_link)
    html_content = response.content
    chapter_link = ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    a_tag = soup.find('a', text="READ NOW")
    if a_tag:
        chapter_link = a_tag.get('href')

        final_file_path = os.path.join(folder_path, 'final')
        index_file_path = os.path.join(folder_path, 'index')
        chapter_1_path = os.path.join(folder_path, '1')
        
        with open(final_file_path, 'w') as final_file:
            final_file.write(f"1||https://readnovelfull.com{chapter_link}")
        
        response1 = requests.get("https://readnovelfull.com" + chapter_link)
        html_content1 = response1.content
        soup1 = BeautifulSoup(html_content1, 'html.parser')
        Log.d("MyTag", html_content1.decode("utf8"))
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
        Log.d("MyTag", image_url)
        img_response = requests.get(image_url)

        image_path = os.path.join(folder_path, 'image.jpg')
        with open(image_path, 'wb') as image_file:
            image_file.write(img_response.content)