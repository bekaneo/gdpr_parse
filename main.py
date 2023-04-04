import json
import requests
from bs4 import BeautifulSoup
import pathlib

path = pathlib.Path('data')
if not path.exists():
    path.mkdir()
   


url = 'https://gdpr-text.com'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
if not pathlib.Path('data/main_page.html').exists():
    with open('data/main_page.html', 'w') as file:
        response = requests.get(url, headers=headers)
        file.write(response.text)
    
with open('data/main_page.html', 'r') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')

main_page_data = soup.find('div', class_='tab-pane').find_all('div', class_='row')
main_page_data = main_page_data[0].find_all('div', class_='col-12')
main_page_data = main_page_data[1]
data_list = []

chapter = main_page_data.find_all('h5')[0].text
chapter_title = main_page_data.find_all('h5')[1].text
data = {
    'chapter': '',
    'chapter_title': '',
    'content': [],
}
content = {
    'section': '',
    'section_title': '',
    'articles': [],
}
articles = {
    'number': '',
    'article_title': '',
    'text': '',
    'eu_gdpr': '',
    'recitals': []
}

recitals = {
    'number': '',
    'text': ''
}

main_page_data = list(main_page_data)[::-1]
for index, tag in enumerate(main_page_data):        
    if tag.name == 'h5' and tag.text.startswith('CHAPTER'):
        data['chapter'] = tag.text.strip()
        data['chapter_title'] = main_page_data[ index - 1 ].text
        if articles['number']:
            content['articles'].append(articles)
        data['content'].append(content)
        data_list.append(data)
        data = {
            'chapter': tag.text.strip(),
            'chapter_title': main_page_data[ index - 1 ].text,
                'content': [],
        }
        content = {
            'section': '',
            'section_title': '',
            'articles': [],
        }
        articles = {
            'number': '',
            'article_title': '',
            'text': '',
            'recitals': []
        }
    elif tag.name == 'h5' and tag.text.startswith('Section'):
        content['section'] = tag.text
        content['section_title'] = main_page_data[index - 1].text
        if articles['number']:
            content['articles'].append(articles)
        data['content'].append(content)
        content = {
            'section': '',
            'section_title': '',
            'articles': [],
        }
        articles = {
            'number': '',
            'article_title': '',
            'text': '',
            'recitals': []
        }
    
    elif tag.name == 'div':
        for inner_tag in tag:
            articles['number'] = inner_tag.text.split('.')[0]
            articles['article_title'] = inner_tag.find('span').text
            link_to_article = inner_tag.find('a').get('href')
            print(f'{articles["number"]}.html {link_to_article} / {len(main_page_data) - index}')
            if not pathlib.Path(f'data/{articles["number"]}.html').exists():
                with open(f'data/{articles["number"]}.html', 'w') as file:
                    response = requests.get(link_to_article, headers=headers)
                    file.write(response.text)
            with open(f'data/{articles["number"]}.html', 'r') as file:
                src = file.read()
            soup = BeautifulSoup(src, 'lxml')
            recital_check = soup.find('div', {'id': 'recital_toggle'})
            article_content = soup.find('div', class_='article_content')
            if recital_check:
                recitals_data = recital_check.find('div', class_='row').find_all('p')

                for recital in recitals_data:
                    if recital.find('b'):
                        recitals['number'] = recital.find('b').text
                    recitals['text'] = ' '.join(recital.text.split())
                    recitals['link'] = recital.find('a').get('href')
                    if recitals:
                        articles['recitals'].append(recitals)
                    recitals = {}

            articles['text'] = ' '.join(article_content.find('div', class_='article_block').text.split())
            articles['eu_gdpr'] =  ' '.join(article_content.find('div', class_='article_info').find('span').next_sibling.text.split())

            content['articles'].append(articles)
            articles = {
                'number': '',
                'article_title': '',
                'text': '',
                'recitals': []
            }
    # if index > 3: 
    #     break

with open('data.json', 'w') as file:
    json.dump(data_list[::-1], file, indent=4)
