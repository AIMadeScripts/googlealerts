import os
import sys
import shutil

# check if feed.txt file exists
if not os.path.exists('feed.txt'):
    print('feed.txt file not found')
    sys.exit()

# remove the articles folder if it already exists
if os.path.exists('articles'):
    shutil.rmtree('articles')

# create a folder to store the articles
os.makedirs('articles')

# read the feed.txt file
with open('feed.txt', 'r') as f:
    # split the file contents into articles
    articles = f.read().split('\n\n')

    # iterate over each article and save it to a file
    for i, article in enumerate(articles):
        # create a new file for the article
        filename = f'articles/{i+1}.txt'
        with open(filename, 'w') as article_file:
            # add ``` to the start of the file
            article_file.write('```\n')
            # write the article to the file
            article_file.write(article)
            # add ``` to the end of the file
            article_file.write('\n```')
