import os
import numpy as np
import json

np.random.seed(69)

def read_json():
    with open('jsons/review_tokens.json') as file:
        data = json.load(file)
    return data

def extract_json(json_data):
    data_set = []

    for item in json_data:
        for review in item.get('reviews', []):
            review_rating = review.get('comment_rating', "")
            review_title = review.get('comment_title', [])
            review_comment = review.get('comment_content', [])

            review_content = review_title + review_comment

            set_item = []
            set_item.append(review_rating)
            set_item.append(review_content)

            data_set.append(set_item)
            print(data_set)

    return data_set

def main():
    data = read_json()
    extract_json(data)



if __name__ == "__main__":
    main()