import os
import random
import re
import subprocess
import feedparser
from typing import List

def get_response(message: str) -> List[str]:
    p_message = message.lower()

    # Extract search term from message using regular expression
    match = re.match(r'^!news\s+(.+)$', p_message)
    if match:
        search_term = match.group(1)

        # Check if news collection is already running
        if os.path.exists('news_collection_in_progress'):
            return ['Sorry, news collection is already in progress. Please wait.']

        # Mark that news collection is in progress
        with open('scripts/news_collection_in_progress', 'w'):
            pass

        try:
            subprocess.run(["google-alerts", "create", "--term", search_term, "--delivery", "rss", "--frequency", "realtime"], check=True)
        except subprocess.CalledProcessError as e:
            os.remove('news_collection_in_progress')
            return ['Error creating Google Alert: ' + str(e)]
            
        files = []

        with open("message.txt", "w") as file:
            file.write("Collecting news sources for you now... please wait")
        
        with open("message.txt", "r") as file:
            if file.readable():
                contents = file.read()
                files.append(contents)
        
        # Remove the file if it already exists
        if os.path.exists("feed.txt"):
            os.remove("feed.txt")

        # Open the file in append mode
        with open("feed.txt", "a") as f:
            # Run the google-alerts list command and capture its output
            try:
                result = subprocess.run(["google-alerts", "list"], capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                return ['Error listing Google Alerts: ' + str(e)]

            # Extract the RSS links from the output using regular expressions
            rss_links = re.findall(r"rss_link\": \"(.*?)\"", result.stdout)

            # Process each RSS link
            for url in rss_links:
                feed = feedparser.parse(url)

                for entry in feed.entries:
                    if search_term.lower() in entry.title.lower() or search_term.lower() in entry.summary.lower():
                        title = entry.title.replace("<b>", "").replace("</b>", "")
                        summary = entry.summary.replace("<b>", "").replace("</b>", "").replace("&nbsp;", " ")
                        link = re.search(r"url=(.*?)&ct", entry.link).group(1)

                        # Write the feed content to the file
                        f.write(f"{title}\n")
                        f.write(f"{link}\n")
                        f.write(f"{summary}\n\n")

        # Run the split.py script to process the feed data into separate article files
        try:
            subprocess.run(["python3", "scripts/split.py"], check=True)
        except subprocess.CalledProcessError as e:
            return ['Error running split.py: ' + str(e)]

        # Send the data from the articles folder
        articles_dir = './articles'  # Update this with the path to your articles folder
        articles = os.listdir(articles_dir)

        files = []
        for article in articles:
            with open(f"{articles_dir}/{article}") as file:
                if file.readable():
                    contents = file.read()
                    # Check if the contents of the file contain at least one alphabetical character
                    if any(char.isalpha() for char in contents):
                        files.append(contents)
                    else:
                        # If the file doesn't contain at least one alphabetical character, remove it
                        os.remove(f"{articles_dir}/{article}")
                        
        # Delete each Google Alert using google-alerts delete command
        try:
            result = subprocess.run(["google-alerts", "list"], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            return ['Error listing Google Alerts: ' + str(e)]

        # Extract the monitor IDs using regular expressions
        monitor_ids = re.findall(r"monitor_id\": \"(.*?)\"", result.stdout)

        for monitor_id in monitor_ids:
            try:
                subprocess.run(["google-alerts", "delete", "--id", monitor_id], check=True)
            except subprocess.CalledProcessError as e:
                return ['Error deleting Google Alert: ' + str(e)]

        return files
        # Mark that news collection is finished
        os.remove('news_collection_in_progress')

    else:
        # Return a default response if the command is not recognized
        return ['Sorry, I didn\'t understand that command.']
        os.remove('news_collection_in_progress')
