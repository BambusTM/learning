import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import emoji
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')

def read_json():
    with open('data.json') as file:
        data = json.load(file)
    return data

def tokenize(data):
    tokenized_reviews = []
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

            tokens = comment_title_tokens + comment_content_tokens
            tokenized_reviews.append({
                "comment_title": comment_title_tokens,
                "comment_content": comment_content_tokens
            })
            
    return tokenized_reviews

def write_json(data, target):
    with open(target, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def remove_stop_words(tokens):
    stop_words_de = set(stopwords.words('german'))
    stop_words_fr = set(stopwords.words('french'))
    stop_words_en = set(stopwords.words('english'))
    stop_words = stop_words_de.union(stop_words_fr).union(stop_words_en)
    punctuation = set(string.punctuation)
    dots = {'..', '...', '....', '.....', '......'}
    punctuation.update(dots)
    
    filtered = [w for w in tokens if w.lower() not in stop_words and w not in punctuation]
    return filtered

def remove_emojis(text):
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in emoji.EMOJI_DATA]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    return clean_text

def word_stem(data):
    stemmer = SnowballStemmer("german")
    stemmed_reviews = []

    for review in data:
        title_tokens = review["comment_title"]
        content_tokens = review["comment_content"]
        
        stemmed_title = [stemmer.stem(word) for word in title_tokens]
        stemmed_content = [stemmer.stem(word) for word in content_tokens]

        stemmed_reviews.append({
            "comment_title": stemmed_title,
            "comment_content": stemmed_content
        })

    write_json(stemmed_reviews, 'word_stem.json')

def word_lemma(data):
    lemmatizer = WordNetLemmatizer()
    lemmatized_reviews = []

    for review in data:
        title_tokens = review["comment_title"]
        content_tokens = review["comment_content"]
        
        lemmatized_title = [lemmatizer.lemmatize(word) for word in title_tokens]
        lemmatized_content = [lemmatizer.lemmatize(word) for word in content_tokens]

        lemmatized_reviews.append({
            "comment_title": lemmatized_title,
            "comment_content": lemmatized_content
        })

    write_json(lemmatized_reviews, 'word_lemma.json')

def main():
    data = read_json()
    tokenized_reviews = tokenize(data)
    write_json(tokenized_reviews, 'review_tokens.json')
    #word_stem(tokenized_reviews)
    #word_lemma(tokenized_reviews)

if __name__ == "__main__":
    main()
