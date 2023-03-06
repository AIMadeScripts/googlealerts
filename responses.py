import os
import random
import re
import subprocess
import feedparser
from typing import List

def get_response(message: str) -> List[str]:
    p_message = message.lower()

    if p_message.startswith('!news '):
        search_term = p_message.split()[1]  # Extract search term from message
        try:
            subprocess.run(["google-alerts", "create", "--term", search_term, "--delivery", "rss", "--frequency", "realtime"], check=True)
        except subprocess.CalledProcessError as e:
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
            subprocess.run(["python3", "split.py"], check=True)
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
                    files.append(contents)

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

    else:
        # Return a default response if the command is not recognized
        return ['Sorry, I didn\'t understand that command.']
