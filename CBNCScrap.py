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
            self.response = response
            url = f"{self.base_url}?query={self.keywords}&sortby=time&p={page}"
            print(url)
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            articles = soup.find_all("div", {"class": "lm_content mt10"})
            # articles = soup.find_all('article')
            
            # print(articles) 

            for ul in articles:
                lu = ul.find('ul', {'class': 'list media_rows middle thumb terbaru gtm_indeks_feed'})
                b = lu.find("li")
                n = b.find("article")
                t = n.find("div",{"class":"box_text"})

                title_element = t.find("h2")
                category_element = t.find("span", {"class": "subjudul"})
                date_element = t.find("span", {"class": "label"})
                href_element = n.find("a")
                
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
            file_name += ".csv"
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
    base_url = f"https://www.cnbcindonesia.com/search"

    scrape = DETIKScraper(keywords, pages)
    response = scrape.fetch(base_url)
    # print(response.text)
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