import unittest
from GlobalNewsCollector.Germany.managerMagazin import managerMagazin
from datetime import date

class TestScrapper(unittest.TestCase):

    def test_get_articles_list(self):
        pass
        # print("Test 1")
        # url = "https://www.manager-magazin.de/"
        # list = managerMagazin.get_articles_list(managerMagazin,url)
        # print(list)
        # self.assertFalse(list == None)
        # for article in list:
        #     self.assertTrue(len(article) > 0)
        #     self.assertIsInstance(article, dict)

        

    def test_get_article(self):
        pass
        # print("Test 2")
        # urlList = managerMagazin.get_articles_list(managerMagazin,"https://www.manager-magazin.de/")
        # print(urlList)
        # url = urlList[0]["url"]
        # e = urlList[0]
        # print(e)
        # url = e['url']
        # print(url)
        # article = managerMagazin.get_article(managerMagazin,url)
        
        # self.assertTrue(len(article) == 8) #Checking that dictionary article contains 8 components. 
        # self.assertIsInstance(article, dict)

        # for item in article: 
        #     self.assertFalse(item == None)
        #     self.assertFalse(item == "") 

        # self.assertTrue(len(article["body"]) > 20)
        
       

if __name__ == '__main__':
    unittest.main()