# import os
# import sys
# sys.path.insert(1, os.path.join(sys.path[0], '..'))
# import BaseCollector
from GlobalNewsCollector import BaseCollector
import requests
from bs4 import BeautifulSoup
from datetime import datetime
class People(BaseCollector.BaseCollector):

    def get_article(self, url: str) -> dict:
        """
        Scrap information from the article that is accessed with parameter url.
        ---
        Args:
            url: The url of the article to scrape.
        Returns: A dictionary containing:\n
                - Date published 
                - Date retrieved
                - Url
                - Author
                - Title
                - Publisher
                - Publisher url
        """
        articleInfo = {}
        sort_webpage = url.strip().replace("http://","").split(".")[0]
        
        # Set to true to implement request lib timeout, set timeout_limit variable to desired limit
        use_timeout = True 
        timeout_limit = 5
        if(use_timeout):
            r = requests.get(url, timeout=timeout_limit)
        else:
            r = requests.get(url)

        # If non-valid link -> return an empty dict that will be ignored
        if r == None:
            return articleInfo


        # Some types of articles have different structures
        if (sort_webpage == "health"):
            soup = BeautifulSoup(r.content, 'html5lib').find('div', attrs={'class': 'articleCont'})
            articleInfo = self.get_health_article(soup, articleInfo)
        elif (sort_webpage == "cpc"):
            soup = BeautifulSoup(r.content, 'html5lib').find('div', attrs={'class': 'p2j_con03 clearfix g-w1200'})
            articleInfo = self.get_cpc_article(soup, articleInfo)
        else:
            soup = BeautifulSoup(r.content, 'html5lib').find('div', attrs={'class': 'layout rm_txt cf'})
            articleInfo = self.get_basic_article(soup, articleInfo)

        # Add shared information thats independent from HTML code
        articleInfo['publisher'] = "Central Committee of the Chinese Communist Party"
        articleInfo['publisher_url'] = "http://www.people.com.cn"
        articleInfo['date_retrieved'] = datetime.utcnow().strftime("%d-%m-%Y %H:%M")
        articleInfo['url'] = url
        return articleInfo
  
    def get_articles_list(self, url: str) -> list:
        """
        Scrap all articles visible in the "Latest news view".
        ---
        Args:
            url: The url of the website.
        Returns: A list containing a dictionary returned from get_article() for each article.
        """
        r = requests.get(url) 
        soup = BeautifulSoup(r.content, 'html5lib')       
        articleList = []
        # Start extraxting articles from the startpage
        listOFArticles = soup.find('div', attrs={'class':'main'})
        for article in listOFArticles.find_all('li'):
            # Try every every found link
            try:
                par = article.find('a', href=True)['href']
                if ("people.com.cn/n" in par):
                        article = self.get_article(par)
                        if (article != {}):
                            articleList.append(article)
                else:
                    continue
            # If link did not match implementeted html structure in get_articles(), move on.
            except Exception:
                continue
        return articleList


    def get_basic_article(self, soup, articleInfo) -> list:
        """
            Handles most article structures.
            ---
            Args:
                soup: The instance of soup for the specific url
                articleInfo: The dictionary related to the specific article
            Returns: 
                The updated version of articleInfo
        """

        # Retrive information under title and extract date published
        try:
            date_source_info = soup.find('div', attrs={'class': 'col-1-1 fl'}).text.strip().split("|")
        except AttributeError:
            date_source_info = soup.find('div', attrs={'class': 'col-1-1'}).text.strip().split("|")
        articleInfo['date_published'] = self.format_time(date_source_info[0])
        articleInfo['author'] = self.extract_author(soup)
        try:
            articleInfo['title'] = soup.find('div', attrs={'class':'col col-1 fl'}).find('h1').text
        except AttributeError:
            articleInfo['title'] = soup.find('div', attrs={'class':'col col-1'}).find('h1').text

        # Extract article info:
        paragraph_table = soup.find('div', attrs={'class':'rm_txt_con cf'})
        body = ""
        # Paragraphs should not have classes
        for paragraph in paragraph_table.find_all('p'):
            try:
                ignore = paragraph['class']
            except KeyError:
                body = body + paragraph.text.strip()
        
        articleInfo['body'] = body
        
        return articleInfo

    def get_health_article(self, soup, articleInfo) -> list:
        """
            Handles health-article structures.
            ---
            Args:
                soup: The instance of soup for the specific url
                articleInfo: The dictionary related to the specific article
            Returns: 
                The updated version of articleInfo
        """
    
        # Retrive information under title and extract date published
        date_and_source = soup.find('div', attrs={'class': 'artOri'})
        date_and_source.find('a').decompose()
        articleInfo['date_published'] = self.format_time(date_and_source.text)
        articleInfo['author'] = self.extract_author(soup)
        articleInfo['title'] = soup.find('div', attrs={'class':'title'}).find('h2').text

        # Extract article info:
        paragraph_table = soup.find('div', attrs={'class':'artDet'})
        body = ""

        for paragraph in paragraph_table.find_all('p'):
            body = body + paragraph.text.strip() 
        articleInfo['body'] = body
        return articleInfo

    def get_cpc_article(self, soup, articleInfo) -> list:
        """
            Function handles specific design of "cpc" links.
            ---
            Args:
                soup: The instance of soup for the specific url
                articleInfo: The dictionary related to the specific article
            Returns: 
                The updated version of articleInfo
        """
        # Retrive information under title and extract date published
        date_and_source = soup.find('p', attrs={'class': 'sou'})
        date_and_source.find('a').decompose().text
        articleInfo['date_published'] = self.format_time(date_and_source)

        # Handle missing author articles
        articleInfo['author'] = self.extract_author(soup)
        articleInfo['title'] = soup.find('div', attrs={'class':'text_c'}).find('h1').text

        # Extract article info:
        paragraph_table = soup.find('div', attrs={'class':'show_text'})
        body = ""

        # Paragraphs should not have classes
        for paragraph in paragraph_table.find_all('p'):
            body = body + paragraph.text.strip() 
        articleInfo['body'] = body
        return articleInfo

    def format_time(self, chinease_time):
        """
            Function converts time through string manipulation
            ---
            Args:
                chinese_time: string of GMT +8 time representation
            Returns: UCT time represented as a string\n
                    
        """
        chinease_time = chinease_time.strip().replace("来源：", "").replace("年","-").replace("月", "-").replace("日"," ")
        time_element = chinease_time.split(" ")
        hour_min_element = time_element[1].split(":")
        uct_hour = str((int(hour_min_element[0]) - 8 )% 24)
        return time_element[0]+" "+uct_hour+":"+hour_min_element[1]

    def extract_author(self, soup):
        """
            Function that extracts the author/editor from an article based on the structure of the html code.
            ---
            Args:
                soup: The instance of soup for the specific url
            Returns: 
                The author
        """
        try:
            return soup.find('div', attrs={'class':'edit cf'}).text.replace("(责编：", "").replace(")","")
        except AttributeError:
            return soup.find('div', attrs={'class':'editor'}).text.replace("(责编：", "").replace(")","")