import json
import math
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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
    normalized_words = [word.lower() for word in word_list]
    return Counter(normalized_words)

def main():
    data = read_json()
    for item in data:
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
    
    def top_words(counter, n = 20):
        if not isinstance(counter, Counter):
            counter = Counter(counter)
        return dict(counter.most_common(n))

    positive_word_filtered = {word: count for word, count in positive_word_occurence.items() if count > 5}
    neutral_word_filtered = {word: count for word, count in neutral_word_occurence.items() if count > 5}
    negative_word_filtered = {word: count for word, count in negative_word_occurence.items() if count > 5}

    total_positive = sum(positive_word_filtered.values())
    total_negative = sum(negative_word_filtered.values())
    total_neutral = sum(neutral_word_filtered.values())

    def normalize(word_count, total_count):
        return {word: count / total_count for word, count in word_count.items()}

    normalized_positive = normalize(positive_word_filtered, total_positive)
    normalized_negative = normalize(negative_word_filtered, total_negative)
    normalized_neutral = normalize(neutral_word_filtered, total_neutral)

    top_positive_words = top_words(normalized_positive)
    top_negative_words = top_words(normalized_negative)
    top_neutral_words = top_words(normalized_neutral)

    data = []
    for word, count in top_positive_words.items():
        data.append([word, count, 'Positive'])
    for word, count in top_negative_words.items():
        data.append([word, count, 'Negative'])
    for word, count in top_neutral_words.items():
        data.append([word, count, 'Neutral'])

    df = pd.DataFrame(data, columns=['Word', 'Relative Occurence', 'Classification'])

    plt.figure(figsize=(12, 8))
    sns.barplot(x='Word', y='Relative Occurence', hue='Classification', data=df)
    plt.xticks(rotation=90)
    plt.title('Top Word Occurrences by Classification')
    plt.show()

    pos_to_neg = sum(top_positive_words.values()) / sum(top_negative_words.values()) if top_negative_words else float('inf')
    neg_to_pos = sum(top_negative_words.values()) / sum(top_positive_words.values()) if top_positive_words else float('inf')

    print(f"Positive to Negative Ratio: {pos_to_neg:.2f}")
    print(f"Negative to Positive Ratio: {neg_to_pos:.2f}")

if __name__ == "__main__":
    main()
