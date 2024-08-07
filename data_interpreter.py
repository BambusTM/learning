import numpy as np
import json
from tqdm import tqdm

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

import torch
import torchvision
import torch.nn as nn
from torchvision import datasets, models, transforms
import os
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(69)

def read_json():
    with open('jsons/review_tokens.json') as file:
        data = json.load(file)
    return data

def extract_json(json_data):
    data_set = []

    total_reviews = sum(len(item.get('reviews', [])) for item in json_data)
    pbar = tqdm(total=total_reviews)

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
            pbar.update(1)

    pbar.close()
    return data_set

def vectorize(data):
    df = pd.DataFrame(data, columns=['rating', 'comments'])
    df['comments'] = df['comments'].apply(lambda x: ' '.join(x))

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['comments'])
    y = df['rating']

    return X, y

def neural_network(X, y):
    model = LogisticRegression(random_state=42)
    model.fit(X, y)
    y_prediction = model.predict(X)
    print("Accuracy:", accuracy_score(y, y_prediction))
    print("Confusion Matrix:\n", confusion_matrix(y, y_prediction))

def main():
    data = read_json()
    training_data = extract_json(data)
    X, y = vectorize(training_data)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("Using: ", device)

    neural_network(X, y)


if __name__ == "__main__":
    main()