from bs4 import BeautifulSoup
import requests
from abc import ABC, abstractmethod
# from GlobalNewsCollector.BaseCollector import BaseCollector
from datetime import datetime

from GlobalNewsCollector.BaseCollector import BaseCollector

class Yicai(BaseCollector):

    def get_articles_list(self, url: str) -> list:

        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')

        articles = soup.find('div', attrs={'id':'headlist'}) # headlist contains the latest 25 articles
        article_list = []

        for article in articles.find_all('a', attrs={'class':'f-db'}, href=True):
            # Sometimes the topmost article is a "live article". Live articles don't seem relevant, thus they're skipped:
            if 'news' in article['href']:
                article_list.append(self.get_article('https://www.yicai.com'+article['href']))

        return article_list
    
    def get_article(self, url: str) -> dict:

        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')

        # date_retrieved = date.today().strftime("%d %b %Y") # current date, can be reformatted

        article_info = soup.find('div', attrs={'class':'title f-pr'}) # article header, used to extract multiple dictionary entries
        title = article_info.h1.text

        # Some articles only have a "Responsible editor", some have "Author", and some have both. Both currently included. 
        author = article_info.find('p', attrs={'class':'names'}).text.replace('\xa0',' ')
        date = article_info.em.text # time in UTC+8, probably

        # text body currently doesn't filter away links and the like but can easily be modified for desired output format:
        paragraphs = soup.find('div', attrs={'id':'multi-text'}) #.text
        text = ''
        if (paragraphs != None):
            for paragraph in paragraphs.find_all('p'):
                text = text + paragraph.text.strip()

        dictionary = {
            'date_published': date,
            'date_retrieved': datetime.utcnow().strftime("%Y-%m-%d"),
            'url' : url,
            'title': title,
            'publisher': 'yicai',
            'publisher_url': 'https://www.yicai.com/',
            'author': author,
            'body': text
        }

        return dictionary