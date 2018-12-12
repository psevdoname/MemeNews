import requests
import requests.auth
import pandas as pd
from newspaper import Article
import praw
from praw.models import MoreComments
import json
import pyimgflip
from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
import nltk
import re
from datetime import timedelta, datetime, date
import time

def scrape_reddit(reddit, engine, limit_, yest):
    try:
        i = 0
        for submission in reddit.subreddit('news').hot(limit=limit_):
            if (submission.created > yest):
                query_comments = '''SELECT EXISTS(SELECT * FROM MemeNews.every_comment  WHERE post_id LIKE '{0}' LIMIT 1)'''.format(submission.id)
                query_articles = '''SELECT EXISTS(SELECT * FROM MemeNews.Daily_Articles  WHERE id LIKE '{0}' LIMIT 1)'''.format(submission.id)
                if (engine.execute(query_articles)):
                    continue
                submission.comment_sort = 'best'
                article = Article(submission.url)
                try:
                    article.download()
                    article.parse()
                    article.nlp()
                    article.fetch_images()
                except:
                    continue
                articles_dict = {
                    "title": re.sub(r'[^\x00-\x7F]', '', submission.title.replace('"', "'")),
                    "score": submission.score,
                    "id": submission.id,
                    "url": submission.url,
                    "comms_num": submission.num_comments,
                    "created": submission.created,
                    "body": re.sub(r'[^\x00-\x7F]', '',article.text.replace('"', "'")),
                    "image": article.top_image,
                    "keywords":', '.join(article.keywords).replace('"', "'"),
                    "summary": re.sub(r'[^\x00-\x7F]', '', article.summary.replace('"', "'"))
                }
                #add articles
                articles_data = pd.DataFrame(articles_dict, index = [i])
                articles_data.to_sql('Daily_Articles', con = engine, if_exists='append', dtype={'None':VARCHAR(5)})
                print("article added")
                if (engine.execute(query_comments)):
                    continue
                comment_dict = {
                    "post_id":[],
                    'post_title':[],
                    "id": [],
                    "author":[],
                    "body":[],
                    "created": [],
                    'score':[],
                    'is_submitter':[],
                    'parent_id':[]}
                for top_level_comment in submission.comments.list()[:100]:
                    try:
                        comment_dict['is_submitter'].append(top_level_comment.is_submitter)
                        comment_dict['post_id'].append(submission.id)
                        comment_dict['id'].append(top_level_comment.id)
                        comment_dict['author'].append(top_level_comment.author)
                        comment_dict['body'].append(re.sub(r'[^\x00-\x7F]', '', top_level_comment.body))
                        comment_dict['score'].append(top_level_comment.score)
                        comment_dict['created'].append(top_level_comment.created_utc)
                        comment_dict['parent_id'].append(top_level_comment.parent_id)
                        comment_dict['post_title'].append(submission.title)
                    except:
                        continue
                comment_data = pd.DataFrame(comment_dict)
                comment_data.to_sql('every_test_comment', con = engine, if_exists='append', dtype={'None':VARCHAR(5)})
                print("comments added")
                i+=1
        return 1
    except:
        return 0

def generateMeme(num, raw, engine, watson_cred, yest, meme_py):
    query = '''SELECT * FROM MemeNews.Daily_Articles WHERE created > {0} ORDER BY score DESC LIMIT {1}'''.format(yest, 2*num)
    df_articles = pd.read_sql(query, engine)
    df = pd.DataFrame(columns = ["post_id", "meme_url", "sentiment"])
    j = 0
    k = 0
    while(j < num+1 and k < df_articles.shape[0]):
        id_ = df_articles["id"][k]
        k+=1
        query = '''SELECT * FROM MemeNews.every_comment WHERE post_id LIKE '{0}' LIMIT 10'''.format(id_)
        df_comments =  pd.read_sql(query, engine)
        if (len(df_comments) < 3):
            continue
        max_emotion_final = [('Joy', -1, df_comments["body"][0]),('Disgust', -1, df_comments["body"][0])]
        for body in df_comments["body"]:
            if (len(body) > 200):
                continue
            resp = extractEntitiesFromComment(body, watson_cred)
            max_emotion = ('emotion', -1, '', 0)
            for r in resp:
                for key, value in r['emotion'].items():
                    if value > max_emotion[1]:
                        max_emotion = (key, value, body, r['sentiment'])
            if max_emotion[3] > 0: #sentiment is positive
                if (max_emotion[1] > max_emotion_final[0][1]):
                    max_emotion_final[0] = max_emotion
            elif max_emotion[1] > max_emotion_final[1][1]: #sentiment is negative
                max_emotion_final[1] = max_emotion
        urls = []
        senti = []
        if (max_emotion_final[0] == max_emotion_final[1]): #same emotion
            query = '''SELECT * FROM MemeNews.Meme_Photos where emotion LIKE '{0}' ORDER BY RAND() LIMIT 2'''.format(max_emotion_1[0])
            df_memes_photos = pd.read_sql(query, engine)
            i = 0
            for meme_photo in df_memes_photos:
                result = meme_py.caption_image(meme_photo, max_emotion_final[i][2], "")
                urls.append(result["url"])
                if i == 0:
                    senti.append('negative')
                else:
                    senti.append('positive')
                i+=1
        else:
            i = 0
            for max_emotion in max_emotion_final:
                query = '''SELECT * FROM MemeNews.Meme_Photos where emotion LIKE '{0}' ORDER BY RAND() LIMIT 1'''.format(max_emotion_final[i][0])
                df_memes_photos = pd.read_sql(query, engine)
                result = meme_py.caption_image(df_memes_photos["id"], max_emotion_final[i][2], "")
                urls.append(result["url"])
                if i == 0:
                    senti.append('negative')
                else:
                    senti.append('positive')
                i+=1

        meme_dict = {"post_id": id_, "meme_url": urls, "sentiment": senti}
        temp = pd.DataFrame(meme_dict, index = [2*j, 2*j+1])
        df = df.append(temp)
        j+=1

    df.to_sql('Memes', con = engine, if_exists='replace', dtype={'None':VARCHAR(5)})
return 1

def extractEntitiesFromUrl(url, watson_cred):
    endpoint_watson = "https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze"
    params = {
        'version': '2017-02-27',
    }
    headers = {
        'Content-Type': 'application/json',
    }

    watson_options = {
      "url": url,
      "features": {
        "entities": {
          "sentiment": True,
          "relevance": True,
        }
      }
    }

    username = watson_cred["username"]
    password = watson_cred["password"]

    resp = requests.post(endpoint_watson,
                         data=json.dumps(watson_options),
                         headers=headers,
                         params=params,
                         auth=(username, password)
                        )
    data=resp.json()
    # create and return a dictionary for each entity with entity name, url, source, relevance and sentiment score as keys
    entities_list=[]
#     print(data)
    for entity in data["entities"]:
        entity_dict={}
        entity_dict["entity"]=entity["text"]
        entity_dict["relevance"]=entity["relevance"]
        entity_dict["sentiment"]=entity["sentiment"]["score"]
        entity_dict["entity"]=entity["text"]
        entities_list.append(entity_dict)

    return entities_list

def extractEntitiesFromComment(comment, watson_cred):
    endpoint_watson = "https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze"
    params = {
        'version': '2017-02-27',
    }
    headers = {
        'Content-Type': 'application/json',
    }

    watson_options = {
      "text": comment,
      "features": {
        "entities": {
          "sentiment": True,
          "relevance": True,
          "emotion" :True,
            'categories': True,
            'semantics': True
        }
      }
    }

    username = watson_cred["username"]
    password = watson_cred["password"]

    resp = requests.post(endpoint_watson,
                         data=json.dumps(watson_options),
                         headers=headers,
                         params=params,
                         auth=(username, password)
                        )
    data=resp.json()
    # create and return a dictionary for each entity with entity name, url, source, relevance and sentiment score as keys
    entities_list=[]
    for entity in data["entities"]:
        entity_dict={}
        try:
            entity_dict["emotion"]=entity["emotion"]
            entity_dict["entity"]=entity["text"]
            entity_dict["relevance"]=entity["relevance"]
            entity_dict["sentiment"]=entity["sentiment"]["score"]
            entities_list.append(entity_dict)
        except:
            continue

    return entities_list
