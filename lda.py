from pandas import Series, DataFrame, Panel
import numpy as np
import requests
import requests.auth
import pandas as pd
from newspaper import Article
import praw
import json
import matplotlib.pyplot as plt

from sklearn.metrics.pairwise import euclidean_distances
#with open('config.json') as f:

with open('config_example.json') as f:
    data = json.load(f)

reddit_cred = data['Reddit']
watson_cred = data['Watson']
newspaper_cred = data['News']
sql_cred = data['SQL']

from sqlalchemy import create_engine
conn_string = 'mysql://{user}:{password}@{host}/{db}?charset=utf8mb4'.format(
    host = sql_cred["host"],
    user = sql_cred["user"],
    password = sql_cred["password"],
    db = 'MemeNews')
engine = create_engine(conn_string)

q = '''select * from every_comment'''

df = pd.read_sql(q, con = engine)
df['created'] = pd.to_datetime(df['created'], unit='s')
documents = list(df.body)

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

no_features = 1000

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(documents)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tf = tf_vectorizer.fit_transform(documents)
tf_feature_names = tf_vectorizer.get_feature_names()
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD


no_topics = 20

# Run NMF
nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

# Run LDA
lda = LatentDirichletAllocation(no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
x_lda = lda.transform(tf)



x_lda = lda.transform(tf)



from sklearn.metrics.pairwise import euclidean_distances
 
def most_similar(x, Z, top_n=5):
    dists = euclidean_distances(x.reshape(1, -1), Z)
    pairs = enumerate(dists[0])
    most_similar = sorted(pairs, key=lambda item: item[1])[:top_n]
    return most_similar

def return_response(text):
	x = lda.transform(tf_vectorizer.transform([text]))[0]
	similarities = most_similar(x, x_lda)
	document_id, similarity = similarities[0]
	return documents[document_id][:1000]
