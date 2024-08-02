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

load_dotenv() 

driver = webdriver.Chrome()
geocoding_api_key = os.getenv("API_KEY")
geocoding_api_base_url = "https://api.geoapify.com/v1/geocode/search?text="

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
base_url = 'https://www.local.ch'
url = 'https://www.local.ch/en/s/Restaurant%20Bern?rid=62b607&sorting=alphanum&page=1'
pages = 1
restaurant_list = []

def find_restaurants(url, pages):
    for p in range(pages):
        page_url = url[:-1] + str(p + 3)
        print(f"##### PAGE {p} #####")
        print("Visiting: ", page_url, "...")
        page = requests.get(page_url, headers = headers)
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
                    restaurant_page_url = a_element.get('href')
                    print("Checking for comments at:", restaurant_page_url, "...")

                    driver.get(base_url + restaurant_page_url)
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "button.detail_showAllCommentsBtn__gpjn_.l--btn.l--btn--tertiary"))
                        )
                        show_more_button = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.detail_showAllCommentsBtn__gpjn_.l--btn.l--btn--tertiary"))
                        )
                        print("button found")
                    except:
                        show_more_button = None
                        print("no button")

                    if show_more_button:
                        driver.execute_script("arguments[0].click();", show_more_button)

                        new_soup = BeautifulSoup(driver.page_source, "html.parser")
                        detailed_results = new_soup.find(id="page-content")
                        popup_div = detailed_results.find("div", class_="l--modal-container-body")
                        WebDriverWait(driver, 10)

                        comment_articles = popup_div.find_all("article")
                    else: 
                        new_soup = BeautifulSoup(driver.page_source, "html.parser")
                        detailed_results = new_soup.find(id="page-content")
                        comment_articles = detailed_results.find_all("article", class_="Reviews_review__LyHOV")


                    for comment in comment_articles:
                        comment_item = []
                        comment_rating = comment.find("span", class_="RatingText_textAverage__eWIer undefined")
                        comment_title = comment.find("h3")
                        paragraphs = comment.find_all("p")

                        for p in paragraphs:
                            if not p.get('class'):
                                comment_content = p

                        comment_date = comment.find("span", class_="Reviews_dateAndAuthor__tnH7_")

                        if not any(comment_title.text.strip() in s for s in review_list):
                            comment_item.append(float(re.sub(r'[^\d.]', '', comment_rating.text.strip())))
                            comment_item.append(comment_title.text.strip())
                            comment_item.append(comment_content.text.strip())
                            comment_item.append(formate_date(comment_date.text.strip()))

                            review_list.append(comment_item)
                
                rating_text = rating_element.text.strip().replace('\u00a0/\u00a05', '') if rating_element else "null"

                if title_element:
                    if not any(title_element.text.strip() in s for s in restaurant_list):
                        restaurant_item = []
                        restaurant_item.append(title_element.text.strip())
                        restaurant_item.append(address_element.text.strip().replace("\u00a0", " "))
                        restaurant_item.append(rating_text)

                        lat, lon = get_coordinates(address_element.text.strip().replace("\u00a0", " "))
                        restaurant_item.append(lat)
                        restaurant_item.append(lon)

                        restaurant_item.append(review_list)

                        restaurant_list.append(restaurant_item)

def formate_date(input_str):
    match = re.search(r'(20\d{2})', input_str)
    if match:
        end_index = match.end()
        date_obj = datetime.strptime(input_str[:end_index], '%B %d, %Y')
        formatted_date = date_obj.strftime('%d.%m.%Y')
        return formatted_date
    return input_str

def get_coordinates(address):
    #address = address.replace(" ", '%20')
    #request_url = f"{geocoding_api_base_url}{address}&apiKey={geocoding_api_key}"
    #headers = CaseInsensitiveDict()
    #headers["Accept"] = "application/json"
    #resp = requests.get(request_url, headers = headers)
    #print("API-STATUS: ", resp.status_code)
    #if resp.status_code == 200:
    #    resp_json = resp.json()
    #    if resp_json['features']:
    #        return resp_json['features'][0]['properties']['lat'], resp_json['features'][0]['properties']['lon']
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
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(formatted_list, file, indent = 4, ensure_ascii=False)

def main():
    find_restaurants(url, pages)
    write_json(restaurant_list)

if __name__ == "__main__":
    main()
