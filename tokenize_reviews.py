from nltk.stem import SnowballStemmer
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import emoji

nltk.download('punkt')
nltk.download('stopwords')

def read_json():
    with open('two_review_data_old.json') as file:
        data = json.load(file)
    return data

def tokenize(data):
    token_list = []
    for item in data:
        for review in item.get('reviews', []):
            comment_title = review.get('comment_title', "")
            comment_content = review.get('comment_content', "")

            comment_title = remove_emojis(comment_title)
            comment_content = remove_emojis(comment_content)

            comment_title_tokens = word_tokenize(comment_title)
            comment_content_tokens = word_tokenize(comment_content)

            comment_title_tokens = remove_stop_words(comment_title_tokens)
            comment_content_tokens = remove_stop_words(comment_content_tokens)

            for token in comment_title_tokens + comment_content_tokens:
                token_list.append([token])

    return token_list

def word_stem(tokens):
    stemmer = SnowballStemmer("german")
    stemmed_list = []

    for word_list in tokens:
        if word_list:
            word = word_list[0]
            stemmed_word = stemmer.stem(word)
            stemmed_list.append([word, stemmed_word])

    write_json(stemmed_list, 'word_stem.json', "word", "stem")

def remove_stop_words(input):
    stop_words_de = set(stopwords.words('german'))
    stop_words_fr = set(stopwords.words('french'))
    stop_words_en = set(stopwords.words('english'))
    stop_words = stop_words_de.union(stop_words_fr).union(stop_words_en)
    punctuation = set(string.punctuation)
    dots = {'..', '...', '....', '.....', '......'}
    punctuation.update(dots)
    
    filtered = [w for w in input if w.lower() not in stop_words and w not in punctuation]

    return filtered

def remove_emojis(input):
    allchars = [str for str in input]
    emoji_list = [c for c in allchars if c in emoji.EMOJI_DATA]
    clean_text = ' '.join([str for str in input.split() if not any(i in str for i in emoji_list)])
        
    return clean_text

def write_json(input, target, title1, title2):
    formatted_list = [
        {
            title1: item[0],
            title2: item[1]
        }
        for item in input if len(item) == 2
    ]
    with open(target, 'w', encoding='utf-8') as file:
        json.dump(formatted_list, file, indent=4, ensure_ascii=False)

def main():
    data = read_json()
    tokens = tokenize(data)
    write_json(tokens, 'review_tokens.json', "token", "stem")
    word_stem(tokens)

if __name__ == "__main__":
    main()
