import requests
from bs4 import BeautifulSoup
import re
import os

def extract_chapter_content(soup, chapter_link):
    content_div = soup.find('div', id='chr-content')
    if not content_div:
        print('Chapter content not found!')
        return None, None

    content_tag = content_div.find('p').find_next_sibling()

    content = []
    while content_tag and content_tag.name != 'div':
        if content_tag.name == 'p':
            content.append(content_tag.get_text(strip=True))
        content_tag = content_tag.find_next_sibling()
    
    a_tag = soup.find('a', href=chapter_link)
    if not a_tag:
        print('Chapter heading not found!')
        return None, None
    chapter_heading = a_tag.get('title')

    return chapter_heading, "\n".join(content)

def curling(chapter_number, base_url, chapter_link, folder_name):
    fail_safe = 0
    
    while chapter_link != "" and fail_safe < 1:
        fail_safe += 1
        url = base_url + chapter_link
        print(url)
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        chapter_heading, extracted_text = extract_chapter_content(soup, chapter_link)
        if not chapter_heading or not extracted_text:
            exit(1)

        link_tag = soup.find('a', id='next_chap')
        if link_tag:
            chapter_link = link_tag.get('href')
            if not chapter_link:
                base_url = webnovel_link
                chapter_link = ""
        else:
            print("Next chapter link not found")
            exit(1)

        with open(f'{folder_name}/{chapter_number}', 'w', encoding='utf-8') as file:
            file.write(chapter_heading + "\n")
            file.write(extracted_text)
        with open('final', 'w') as f:
            f.write(str(chapter_number) + '||' + url)        
        chapter_number+=1

def downloadChapters(base_url, webnovel_link):
    folder_name = webnovel_link.split(".")[1].split("/")[-1]
    start = 0
    
    if os.path.isdir(folder_name):
        with open('final', 'r') as f:
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
                print(chapter_link)
            else:
                print("Next chapter link not found")
                exit(1)
    else:
        os.mkdir(folder_name)
        response = requests.get(webnovel_link)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        a_tag = soup.find('a', text="READ NOW")
        if a_tag:
            chapter_link = a_tag.get('href')
        else:
            print("Chapter 1 link not found!!")
            exit(1)

        start = 1

    curling(start, base_url, chapter_link, folder_name)

if __name__ == "__main__":
    webnovel_link = 'https://readnovelfull.com/reverend-insanity-v1.html'
    base_url = 'https://readnovelfull.com'
    downloadChapters(base_url, webnovel_link)
