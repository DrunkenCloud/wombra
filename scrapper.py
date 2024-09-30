import requests
from bs4 import BeautifulSoup
import re
import os

def curling(chapter_begin : int, chapter_end : int, base_url : str, chapter_link : str, folder_name : str, previous_link : str):
    if (chapter_begin <= 0 or chapter_end <= 0):
        return
    
    prev_chapter = ""
    temp_prev = ""
    
    for i in range(chapter_begin, chapter_end):
        if (os.path.exists(f'{folder_name}/chapter-{i}')):
            all_files = os.listdir(folder_name)
            while(os.path.exists(f'{folder_name}/chapter-{i}')):
                i += 1
            if (i >= chapter_end):
                return
            with open(f'{folder_name}/chapter-{i - 1}', 'r') as file:
                for j,line in enumerate(file):
                    if j == 2:
                        temp_prev = line.rstrip()
                    if j == 3:
                        chapter_link = line.split(base_url)[1].rstrip()
                        break

        file_name = f'chapter-{i}'

        url = base_url + chapter_link
        print(url)
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        if (i == chapter_begin):
            prev_chapter = previous_link
        else:
            prev_chapter = temp_prev

        a_tag = soup.find('a', href=chapter_link)
        if (a_tag):
            chapter_heading = a_tag.get('title')
        else:
            print("Heading not found!!")
            exit(1)
        link_tag = soup.find('a', id='next_chap')
        if link_tag:
            temp_prev = base_url + chapter_link
            chapter_link = link_tag.get('href')
            print(chapter_link)
        else:
            print("Link not found")
            exit(1)

        with open(f'{folder_name}/{file_name}', 'w', encoding='utf-8') as file:
            file.write(chapter_heading + "\n")
            file.write(prev_chapter + "\n")
            file.write(temp_prev + "\n")
            file.write(base_url + chapter_link + "\n")
        
        curr_chapter_instances = soup.find_all(string=lambda text: f'Chapter {i}' in text)
        if len(curr_chapter_instances) >= 2:
            second_last = curr_chapter_instances[-2]

            paragraph_tag = second_last.find_next('p')

            content = []
            while paragraph_tag and paragraph_tag.name != 'div':
                content.append(paragraph_tag.get_text(strip=True))
                paragraph_tag = paragraph_tag.find_next_sibling()

            extracted_text = "\n".join(content)
            with open(f'{folder_name}/{file_name}', 'a', encoding='utf-8') as file:
                file.write(extracted_text)
        else:
            print(f'Not enough occurrences of "Chapter {i}" found.')
            exit(1)

def downloadChapters(base_url : str, webnovel_link : str):
    folder_name = webnovel_link.split(".")[1].split("/")[-1]
    start = 1
    chapter_link = ""
    if (os.path.isdir(folder_name)):
        all_files = os.listdir(folder_name)
        while(True):
            if f'chapter-{start}' not in all_files:
                break
            start += 1
        with open(f'{folder_name}/chapter-{start - 1}', 'r') as file:
            for i,line in enumerate(file):
                if i == 2:
                    webnovel_link = line.rstrip()
                if i == 3:
                    chapter_link = line.split(base_url)[1].rstrip()
                    break
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

    print(base_url + chapter_link)
    curling(start, start+10, base_url, chapter_link, folder_name, webnovel_link)


if __name__ == "__main__":
    webnovel_link = 'https://readnovelfull.com/reverend-insanity-v1.html'
    base_url = 'https://readnovelfull.com'
    downloadChapters(base_url, webnovel_link)