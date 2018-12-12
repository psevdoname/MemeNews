<<<<<<< HEAD
from lda import return_response

chatHistory={}
@app.route('/AskReddit', methods=['GET', 'POST'])
def askReddit():
	return render_template('MemeNews_askReddit.html', chatHistory=chatHistory)
@app.route('/ChatReddit', methods=['GET', 'POST'])
def chatReddit():	
	if request.method== 'GET':
		return redirect('/AskReddit')
	userInput=request.form['userInput']
	output="Huh, you don't want to talk!?"
	if userInput:
		output=return_response(userInput)
		chatHistory[userInput]=output
	return render_template('MemeNews_askReddit.html',userInput=userInput, output=output,chatHistory=chatHistory)
		
from flask import Flask, Markup, render_template, request, session, url_for, redirect
import datetime
from sqlalchemy import create_engine
import pandas as pd
import json
app = Flask(__name__)

#AUTH 
with open('config.json') as f:
    data = json.load(f)
reddit_cred = data['Reddit']
watson_cred = data['Watson']
newspaper_cred = data['News']
sql_cred = data["SQL"]
img_cred = data["img"]

#SQL
conn_string = 'mysql://{user}:{password}@{host}/{db}?charset=utf8mb4'.format(
    host = sql_cred["host"], 
    user = sql_cred["user"],
    password = sql_cred["password"], 
    db = 'MemeNews')
engine = create_engine(conn_string)

#grab the memes & the associated article
query = '''SELECT * FROM MemeNews.Memes'''
df_memes_ = pd.read_sql(query, engine)
df_dict = {}
for index, row in df_memes_.iterrows():
    if (index %2 ==0): 
        query = '''SELECT * FROM MemeNews.Daily_Articles WHERE id LIKE '{0}' LIMIT 1'''.format(row['post_id'])
        df_article = pd.read_sql(query, engine)
        df_dict = df_article.iloc[0].to_dict()
        print(df_dict['title'], df_dict['url'], df_dict['image'], df_dict['body'])
        

@app.route('/', methods=['GET', "POST"])
def main():
	return render_template('index.html')

@app.route('/articles', methods=['GET', "POST"])
def article():
	return render_template('articles.html')

@app.route('/meme', methods=['GET', "POST"])
def articles():
	return render_template('meme.html')

if __name__ == "__main__":
    app.run(debug=True)
=======
from flask import Flask, Markup, render_template, request, session, url_for, redirect
import pymysql.cursors, datetime
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
	userInput=request.args.getlist('userInput');
	return render_template('askReddit.html',userInput=userInput)




if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> 9b5b5cab388a93752f3849f3a1942667c807a9ad
