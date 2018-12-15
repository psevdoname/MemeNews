# MemeTimes
Team Members: Jaisal Friedman, Ashley Tsoi, Artem Dovzhenko, Komiljon Turdaliyev
Project Submission Hosted on VM at: http://35.199.18.22:8888/tree/MemeNews

## Code Base
1. 'flask_app.py' : flask python script that runs server in development. This is where the front-end connects to the databases and scripts
2. scripts -> 'lda.py', 'scrape_missing_comments.py', 'daily_articles.py'
3. dev_notebooks -> the most Jupyter Files relevant are:
4. templates & static -> HTML/CSS/JS folders for front-end

## Usage
1. Cron processes : run 'daily_articles' each day and 'scrape_missing_comments' each week to update data-base and meme generation
2. Flask server : calls lda.py and make_plot_for.py to generate lda models on comments & articles displayed.

## Back-end Architecture
1. MySQL
  1. MySQL database: Tables - Daily_Articles, every_comment, Memes, Meme_Photos
  2. MySQL non-production Tables: Daily_Test_Articles, every_test_comment, Memes_Test (used for testing/development)
2. Explanation
  1. Daily_Articles: stores Articles information
  2. every_comment: stores all comments pulled from articles
  3. Memes: stores final memes generated with each cron runs
  4. Meme_Photos: stores meme photos with tagged emotion to be matched with Meme comments

## Front-end
1. Bootstrap & HTML/CSS custom design

## Scripts
1. daily_articles.py
  - script that calls scrape reddit function and generate meme.
  - to be run each day to populate database with new Memes
2. functions.py
  - holds watson API interaction, meme generation, and scrape reddit for articles & comments.
3. lda.py
  - generates an lda model from a portion of the current comments in the database
4. scrape_missing_comments.py
  - checks for articles that do not have comments and re-scrapes reddit to populate database.

## Dependencies & APIs
1. nltk - create LDA
2. pyLDAvis - visualize LDA
3. pyimgflip.py - imglip API
4. PRAW - python reddit API wrapper
5. Watson API

## Notes
1. the start-up of the server is relatively slow.
2. some of the front-end is not perfect, however. that is not the point of the class.
3. the ask reddit is more like a chat-bot.
4. if you'd like to run code on your own credentials edit the 'config-example.json' file and change its name
