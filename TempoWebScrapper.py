import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pprint import pprint

class DETIKScraper:
    def __init__(self, keywords, pages):
        self.keywords = keywords
        self.pages = pages

    def fetch(self, base_url):
        self.base_url = base_url

        self.params = {
            'query': self.keywords,
            'sortby': 'time',
            'page': 2
        }

        self.headers = {
            'sec-ch-ua': '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-platform': "Linux",
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.35 Safari/537.36'
        }

        self.response = requests.get(self.base_url, params=self.params, headers=self.headers)

        return self.response

    def get_articles(self, response):
        article_lists = []

        for page in range(1, int(self.pages)+1):
            self.params['page'] = page
            self.response = requests.get(self.base_url, params=self.params, headers=self.headers)
            url = f"{self.base_url}?q={self.keywords}&sortby=time&page={page}"
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            articles = soup.find_all('article')
            for article in articles:
                title_element = article.find("h2", {"class": "title"})
                category_element = article.find("span", {"class": "kanal cl-dark"})
                date_element = article.find("h4", {"class": "date"})
                href_element = article.find("a")
                
                title = title_element.get_text() if title_element else "Title not found"
                category = category_element.get_text() if category_element else "Category not found"
                published_time = date_element.get_text() if date_element else "Date not found"
                href = href_element["href"] if href_element and "href" in href_element.attrs else "Href not found"
                article_lists.append({
                        "title": title, 
                        "cateogory": category, 
                        "published_time": published_time, 
                        "href": href
                        })

        self.articles = article_lists

        try:
            self.show_results() 
        except Exception as e:
            print(e)
        finally:
            print()
            print( "[~] Scraping finished!")
            print(f"[~] Total Articles: {len(self.articles)}")

        return self.articles

    def save_to(self, file_format="csv"):
        '''  '''
        time_scrape = datetime.now().strftime("%Y-%m-%dT%H.%M.%S")

        df = pd.DataFrame(self.articles)

        file_name = f"./result_{self.keywords}_{time_scrape}"
        if file_format == "csv":
            file_name += "Tempo.csv"
            df.to_csv(path_or_buf=file_name, index=False)
            print(f"[~] Result saved to '{file_name}'")
        elif file_format == "excel":
            file_name += ".xlsx"
            df.to_excel(file_name, index=False)
            print(f"[~] Result saved to '{file_name}'")

    def show_results(self, row = 5):
        df = pd.DataFrame(self.articles)
        df.index += 1
        if row:
            print(df.head())
        else:
            print(df)

if __name__ == '__main__':
    keywords = input("[~] Keywords     : ")
    pages =    input("[~] Total Pages  : ")
    base_url = f"https://www.tempo.co/search"

    scrape = DETIKScraper(keywords, pages)
    response = scrape.fetch(base_url)
    articles = scrape.get_articles(response)

    try:
        ask =             input("[~] Do you want save the results? [y/n]: ").lower()
        if ask == 'y':
            file_format = "csv"
            scrape.save_to(file_format=file_format)
        elif ask == 'n':
            scrape.show_results()
    except Exception as e:
        print(e)
    finally:
        print("[~] Program Finished")