import json
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize

token_list = []

def read_json():
    with open('two_review_data_old.json') as file:
        data = json.load(file)
    return data

def tokenize(data):
    for item in data:
        for review in item.get('reviews'):
            comment_title: str = review.get('comment_title')
            comment_content: str = review.get('comment_content')

            title_tokens = word_tokenize(comment_title)
            comment_tokens = word_tokenize(comment_content)

            review_item = []
            review_item.append(title_tokens)
            review_item.append(comment_tokens)

            token_list.append(review_item)

    return token_list

def write_json(input):
    formatted_list = [
        {
            "title": item[0],
            "comment": item[1]
        }
        for item in input
    ]
    with open('review_tokens.json', 'w', encoding='utf-8') as file:
        json.dump(formatted_list, file, indent = 4, ensure_ascii=False)

def main():
    data = read_json()
    tokens = tokenize(data)
    write_json(tokens)
    print(tokens)

if __name__ == "__main__":
    main()
