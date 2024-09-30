import requests
from bs4 import BeautifulSoup
import re
import os

def extract_previous_chapter_info(folder_name, start, base_url):
    chapter_link = ""
    previous_link = ""
    if os.path.exists(f'{folder_name}/chapter-{start - 1}'):
        with open(f'{folder_name}/chapter-{start - 1}', 'r') as file:
            for i, line in enumerate(file):
                if i == 2:
                    previous_link = line.rstrip()
                if i == 3:
                    chapter_link = line.split(base_url)[1].rstrip()
                    break
    return chapter_link, previous_link

def extract_chapter_content(soup, i):
    curr_chapter_instances = soup.find_all(string=lambda text: f'Chapter {i}' in text)
    if len(curr_chapter_instances) >= 2:
        second_last = curr_chapter_instances[-2]
        paragraph_tag = second_last.find_next('p')
        content = []
        while paragraph_tag and paragraph_tag.name != 'div':
            content.append(paragraph_tag.get_text(strip=True))
            paragraph_tag = paragraph_tag.find_next_sibling()
        return "\n".join(content)
    else:
        print(f'Not enough occurrences of "Chapter {i}" found.')
        exit(1)

def curling(chapter_begin, chapter_end, base_url, chapter_link, folder_name, previous_link):
    temp_prev = ""
    
    for i in range(chapter_begin, chapter_end):
        if os.path.exists(f'{folder_name}/chapter-{i}'):
            while os.path.exists(f'{folder_name}/chapter-{i}'):
                i += 1
            if i >= chapter_end:
                return
            chapter_link, temp_prev = extract_previous_chapter_info(folder_name, i, base_url)

        file_name = f'chapter-{i}'
        url = base_url + chapter_link
        print(url)
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        prev_chapter = previous_link if i == chapter_begin else temp_prev

        a_tag = soup.find('a', href=chapter_link)
        chapter_heading = a_tag.get('title') if a_tag else "Heading not found!!"
        
        link_tag = soup.find('a', id='next_chap')
        if link_tag:
            temp_prev = base_url + chapter_link
            chapter_link = link_tag.get('href')
            print(chapter_link)
        else:
            print("Next chapter link not found")
            exit(1)

        with open(f'{folder_name}/{file_name}', 'w', encoding='utf-8') as file:
            file.write(chapter_heading + "\n")
            file.write(prev_chapter + "\n")
            file.write(temp_prev + "\n")
            file.write(base_url + chapter_link + "\n")

        extracted_text = extract_chapter_content(soup, i)
        with open(f'{folder_name}/{file_name}', 'a', encoding='utf-8') as file:
            file.write(extracted_text)

def downloadChapters(base_url, webnovel_link):
    folder_name = webnovel_link.split(".")[1].split("/")[-1]
    
    start = 1
    if os.path.isdir(folder_name):
        all_files = os.listdir(folder_name)
        while True:
            if f'chapter-{start}' not in all_files:
                break
            start += 1
        
        chapter_link, previous_link = extract_previous_chapter_info(folder_name, start, base_url)
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

        previous_link = webnovel_link

    print(base_url + chapter_link)
    curling(start, start + 10, base_url, chapter_link, folder_name, previous_link)

if __name__ == "__main__":
    webnovel_link = 'https://readnovelfull.com/reverend-insanity-v1.html'
    base_url = 'https://readnovelfull.com'
    downloadChapters(base_url, webnovel_link)
