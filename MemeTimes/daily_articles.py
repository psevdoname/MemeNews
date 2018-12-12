from functions import *

#open config file
with open('config.json') as f:
    data = json.load(f)
reddit_cred = data['Reddit']
watson_cred = data['Watson']
newspaper_cred = data['News']
sql_cred = data["SQL"]
img_cred = data["img"]

#Authentification
reddit = praw.Reddit(**reddit_cred)
meme_py = pyimgflip.Imgflip(username=img_cred["username"], password=img_cred["password"])

#Connect to Database
conn_string = 'mysql://{user}:{password}@{host}/{db}?charset=utf8mb4'.format(
    host = sql_cred["host"],
    user = sql_cred["user"],
    password = sql_cred["password"],
    db = 'MemeNews')
engine = create_engine(conn_string)

#get 24 hours ago
yest = (datetime.utcnow()-timedelta(hours = 24)).timestamp()

scrape_status = scrape_reddit(reddit, engine, 20, yest)
if (scrape_status):
    meme_status = generateMeme(2, True, engine, watson_cred, yest, meme_py)
    if (not meme_status):
        print("Meme Generation Failed")
else:
    print("Scrape Failed")
