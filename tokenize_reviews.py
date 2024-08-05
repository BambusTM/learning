import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

token_list = []

def read_json():
    with open('two_review_data_old.json') as file:
        data = json.load(file)
    return data

def tokenize(data):
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

    for item in data:
        for review in item.get('reviews'):
            comment_title: str = review.get('comment_title')
            comment_content: str = review.get('comment_content')

            title_tokens = word_tokenize(comment_title)
            comment_tokens = word_tokenize(comment_content)

            stop_title_tokens = remove_stop_words(title_tokens)
            stop_title_tokens = remove_stop_words(comment_tokens)

            review_item = []
            review_item.append(stop_title_tokens)
            review_item.append(stop_title_tokens)

            token_list.append(review_item)

    return token_list

def remove_stop_words(word_tokens):
    nltk.download('stopwords')
    
    stop_words_de = set(stopwords.words('german'))
    stop_words_fr = set(stopwords.words('french'))
    stop_words_en = set(stopwords.words('english'))
    stop_words = stop_words_de.union(stop_words_fr).union(stop_words_en)
    punctuation = set(string.punctuation)
    
    filtered = [w for w in word_tokens if w.lower() not in stop_words and w not in punctuation]

    return filtered

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

if __name__ == "__main__":
    main()
