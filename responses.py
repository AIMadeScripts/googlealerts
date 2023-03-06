import os
import random
from typing import List

def get_response(message: str) -> List[str]:
    p_message = message.lower()

    if p_message == '!post_feed':
        articles_dir = './articles'  # Update this with the path to your articles folder
        articles = os.listdir(articles_dir)

        files = []
        # Create a list of file names
        # file_names = [f"Found file: {file_name}" for file_name in articles]
        
        for article in articles:
            with open(f"{articles_dir}/{article}") as file:
                if file.readable():
                    contents = file.read()
                    files.append(contents)
        # Return list of file contents
        return files
    else:
        # Return a default response if the command is not recognized
        return ['Sorry, I didn\'t understand that command.']
