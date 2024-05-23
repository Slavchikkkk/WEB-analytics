import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta


def fetch_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    news_items = soup.find_all('div', class_='article_news_list')    
    news_list = []

    for item in news_items:
        try:
            title = item.find('a').text.strip()
            print(title)
        except:
            title = None
        try:
            link = item.find('a')['href']
            print(link)
        except:
            link = None
        try:    
            date_time = item.find('div', class_='article_time').text.strip()
            print(date_time)
        except:
            date_time = None   
        
        if link:
            author, views = fetch_author_and_views(link)
            print(author)
            print(views)
        else:
            author = views = None

        news_list.append({
            'Title': title,
            'Date': date_time,
            'Link': link,
            'Author': author,
            'Views': views
        })
    return news_list

def fetch_author_and_views(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        author = soup.find('span', class_='post__author').text.strip() if soup.find('span', class_='post__author') else None
        views = soup.find('div', class_='post__views').text.strip() if soup.find('div', class_='post__views') else None
    except Exception as e:
        author = views = None
    return author, views


def generate_date_urls(start_date, num_days):
    base_url = 'https://www.pravda.com.ua/news/date_'
    urls = []
    current_date = start_date
    for i in range(num_days):
        date_str = current_date.strftime('%d%m%Y')
        urls.append(f'{base_url}{date_str}/')
        current_date -= timedelta(days=1)
    return urls



if __name__ == "__main__":
    start_date = datetime.today()
    num_days_to_scrape = 50  # The number of days based on the total number of news to collect
    date_urls = generate_date_urls(start_date, num_days_to_scrape)

    news_data = []
    for i, url in enumerate(date_urls):
        print(f'Scraping page for date {url}')
        news_data.extend(fetch_news(url))
        time.sleep(1)  # Pause to prevent overwhelming the server

    # Save data to CSV
    df = pd.DataFrame(news_data)
    df.to_csv('news_data.csv', index=False)
    print('Data saved to news_data.csv')


