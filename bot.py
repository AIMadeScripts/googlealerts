import discord
import responses
import asyncio
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


async def send_message(message, user_message, is_private):
    try:
        response = responses.get_response(user_message)
        for article in response:
            await message.author.send(article) if is_private else await message.channel.send(article)
            await asyncio.sleep(2) # sleep for 2 seconds between sending each article

    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = 'MTA4MjA3ODE3MzgxNjE4MDg1OA.G-bnKG.gVpxfA5Y20wYh04SjV2wb4uOXRGyrocyk3eXm8'
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

if __name__ == '__main__':
    run_discord_bot()
