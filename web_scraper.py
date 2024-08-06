import json
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

load_dotenv()

geocoding_api_key = os.getenv("API_KEY")
geocoding_api_base_url = "https://api.geoapify.com/v1/geocode/search?text="

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
base_url = 'https://www.local.ch'
url = 'https://www.local.ch/en/s/Restaurant%20Bern?rid=62b607&sorting=alphanum&page=1'
pages = 32

def find_restaurants(url, pages, base_url):
    restaurant_list = []

    for p in range(pages):
        page_url = url[:-1] + str(p + 1)
        print(f"##### PAGE {p} #####")
        print("Visiting: ", page_url, "...")
        page = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="page-content")
        wrapper_elements = results.find_all("div", class_="SearchResultList_list__5Xa0I")

        for wrapper in wrapper_elements:
            restaurant_elements = wrapper.find_all("div", class_="SearchResultList_listElementWrapper__KRuKD")
            for element in restaurant_elements:
                review_list = []
                title_element = element.find("h2", class_="l--link ListElement_titleHeadline__sAf_l")
                address_element = element.find("address")
                rating_wrapper = element.find("div", class_="Rating_ratingWrapper__WYkPQ")

                rating_element = None
                if rating_wrapper:
                    rating_element = rating_wrapper.find("span", class_="RatingText_textAverage__eWIer RatingText_default__z4Cim")

                    a_element = element.find("a", class_="ListElement_link__LabW8")
                    detail_url = base_url + a_element.get('href')
                    print("Checking for comments at:", detail_url, "...")

                    options = Options()
                    options.headless = True
                    options.add_argument("--headless=new")
                    options.add_argument("--disable-extensions")
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                    try:
                        driver.get(detail_url)

                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                        ).click()

                        try:
                            show_comments_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Show all comments']"))
                            )
                            show_comments_button.click()
                            time.sleep(3)

                            new_soup = BeautifulSoup(driver.page_source, 'html.parser')
                            review_elements = new_soup.find_all('article', class_="Reviews_review__LyHOV")

                            for review in review_elements:
                                title_element = review.find('h3')
                                review_text_element = review.find('p', recursive=False)
                                span_element = review.find('span', class_="Reviews_dateAndAuthor__tnH7_")
                                rating = review.find('span', class_="RatingText_textAverage__eWIer")

                                if span_element:
                                    text = span_element.get_text(strip=True)
                                    if '|' in text:
                                        date, author = text.split('|')
                                        date = date.strip()
                                        author = author.strip()
                                    else:
                                        date = author = None

                                if title_element and review_text_element and rating:
                                    review_item = [
                                        float(re.sub(r'[^\d.]', '', rating.get_text(strip=True))),
                                        title_element.get_text(strip=True),
                                        review_text_element.get_text(strip=True),
                                        formate_date(date)
                                    ]

                                    if review_item not in review_list:
                                        review_list.append(review_item)

                        except:
                            print("Error clicking on 'Show all comments'")
                    except:
                        print("Error processing comments")
                    finally:
                        driver.quit()

                rating_text = rating_element.text.strip().replace('\u00a0/\u00a05', '') if rating_element else "null"

                if title_element and address_element:
                    if not any(title_element.text.strip() in s for s in restaurant_list):
                        restaurant_item = [
                            title_element.text.strip(),
                            address_element.text.strip().replace("\u00a0", " "),
                            rating_text
                        ]

                        lat, lon = get_coordinates(address_element.text.strip().replace("\u00a0", " "))
                        restaurant_item.extend([lat, lon, review_list])

                        restaurant_list.append(restaurant_item)

    return restaurant_list

def formate_date(input_str):
    match = re.search(r'(20\d{2})', input_str)
    if match:
        end_index = match.end()
        date_obj = datetime.strptime(input_str[:end_index], '%B %d, %Y')
        formatted_date = date_obj.strftime('%d.%m.%Y')
        return formatted_date
    return input_str

def get_coordinates(address):
    address = address.replace(" ", '%20')
    request_url = f"{geocoding_api_base_url}{address}&apiKey={geocoding_api_key}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    resp = requests.get(request_url, headers = headers)
    print("API-STATUS: ", resp.status_code)
    if  resp.status_code == 200:
        resp_json = resp.json()
        if resp_json['features']:
            return resp_json['features'][0]['properties']['lat'], resp_json['features'][0]['properties']['lon']
    return None, None

def write_json(item_list):
    formatted_list = [
        {
            "name": item[0],
            "address": item[1],
            "rating": item[2],
            "lat": item[3],
            "lon": item[4],
            "reviews": [
                {
                    "comment_rating": review[0],
                    "comment_title": review[1],
                    "comment_content": review[2],
                    "comment_date": review[3]
                }
                for review in item[5]
            ]
        }
        for item in item_list
    ]
    with open('jsons/data.json', 'w', encoding='utf-8') as file:
        json.dump(formatted_list, file, indent=4, ensure_ascii=False)

def main():
    restaurant_list = find_restaurants(url, pages, base_url)
    write_json(restaurant_list)

if __name__ == "__main__":
    main()
