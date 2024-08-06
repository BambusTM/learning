import json
import math
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

positive_word_occurence = Counter()
neutral_word_occurence = Counter()
negative_word_occurence = Counter()

class Classification:
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'
    NEGATIVE = 'negative'

def read_json():
    with open('jsons/review_tokens.json') as file:
        data = json.load(file)
    return data

def classify_review(rating):
    if rating:
        if math.isclose(rating, 3.5, abs_tol=0.00001) or rating > 3.5:
            return Classification.POSITIVE
        elif math.isclose(rating, 2.5, abs_tol=0.00001) or rating > 2.5:
            return Classification.NEUTRAL
        else:
            return Classification.NEGATIVE
    else:
        print("unable to classify")
        return None

def count_words(word_list):
    return Counter(word_list)

def main():
    data = read_json()
    for item in data:
        print()
        restaurant_name = item.get('restaurant_name', "")
        restaurant_rating = item.get('restaurant_rating', "")

        for comment in item.get('reviews', []):
            comment_rating = comment.get('comment_rating', "")
            comment_title = comment.get('comment_title', [])
            comment_content = comment.get('comment_content', [])

            comment_classification = classify_review(comment_rating)
            if comment_classification is None:
                continue

            title_word_count = count_words(comment_title)
            content_word_count = count_words(comment_content)

            if comment_classification == Classification.POSITIVE:
                positive_word_occurence.update(title_word_count)
                positive_word_occurence.update(content_word_count)
            elif comment_classification == Classification.NEUTRAL:
                neutral_word_occurence.update(title_word_count)
                neutral_word_occurence.update(content_word_count)
            elif comment_classification == Classification.NEGATIVE:
                negative_word_occurence.update(title_word_count)
                negative_word_occurence.update(content_word_count)
    
    positive_word_filtered = {word: count for word, count in positive_word_occurence.items() if count > 5}
    neutral_word_filtered = {word: count for word, count in neutral_word_occurence.items() if count > 5}
    negative_word_filtered = {word: count for word, count in negative_word_occurence.items() if count > 5}

    data = []
    for word, count in positive_word_filtered.items():
        data.append([word, count, 'Positive'])
    for word, count in neutral_word_filtered.items():
        data.append([word, count, 'Neutral'])
    for word, count in negative_word_filtered.items():
        data.append([word, count, 'Negative'])

    import pandas as pd
    df = pd.DataFrame(data, columns=['Word', 'Count', 'Classification'])

    plt.figure(figsize=(12, 8))
    sns.barplot(x='Word', y='Count', hue='Classification', data=df)
    plt.xticks(rotation=90)
    plt.title('Word Occurrences by Classification')
    plt.show()

if __name__ == "__main__":
    main()
