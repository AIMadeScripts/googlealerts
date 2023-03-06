import os
import subprocess
import re
import time
import feedparser
import discord
import shutil
import asyncio
import responses
import threading

def request_feed():
    # Remove the file if it already exists
    if os.path.exists("feed.txt"):
        os.remove("feed.txt")

    # Open the file in append mode
    with open("feed.txt", "a") as f:
        # Run the google-alerts list command and capture its output
        result = subprocess.run(["google-alerts", "list"], capture_output=True, text=True)

        # Extract the RSS links from the output using regular expressions
        rss_links = re.findall(r"rss_link\": \"(.*?)\"", result.stdout)

        # Process each RSS link
        for url in rss_links:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.title.replace("<b>", "").replace("</b>", "")
                summary = entry.summary.replace("<b>", "").replace("</b>", "").replace("&nbsp;", " ")
                link = re.search(r"url=(.*?)&ct", entry.link).group(1)

                # Write the feed content to the file
                f.write(f"{title}\n")
                f.write(f"{link}\n")
                f.write(f"{summary}\n\n")

def run_discord_bot():
    # read the token from file
    token_file = os.path.expanduser('~/.config/google_alerts/discordtoken')
    if not os.path.exists(token_file):
        TOKEN = input("Please enter your Discord bot token: ")
        with open(token_file, 'w') as f:
            f.write(TOKEN)
    else:
        with open(token_file, 'r') as f:
            TOKEN = f.read().strip()

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if user_message[0] == '?':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    client.run(TOKEN)

async def send_message(message, user_message, is_private):
    try:
        response = responses.get_response(user_message)
        for article in response:
            await message.author.send(article) if is_private else await message.channel.send(article)
            await asyncio.sleep(2) # sleep for 2 seconds between sending each article

    except Exception as e:
        print(e)

def main():
    print("What do you want to do?")
    print("1. Request a new feed now.")
    print("2. Automate a feed request every hour.")
    print("3. Run with the current feed.")
    choice = input("Enter your choice: ")

    if choice == '1':
        request_feed()
        os.system('python3 split.py')
    elif choice == '2':
        # Start a separate thread to run the request_feed() function every hour
        feed_thread = threading.Thread(target=run_request_feed, daemon=True)
        feed_thread.start()
    elif choice == '3':
        os.system('python3 split.py')
        pass
    else:
        print("Invalid choice.")
        sys.exit()
    run_discord_bot()

def run_request_feed():
    while True:
        request_feed()
        while not os.path.exists('feed.txt'):
            time.sleep(1)
        os.system('python3 split.py')
        time.sleep(3599) # wait for an hour minus 1 second

if __name__ == '__main__':
    main()
