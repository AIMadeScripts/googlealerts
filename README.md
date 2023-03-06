# googlealerts
Manager for Google Alerts

Simply run
1. ```git clone https://github.com/AIMadeScripts/googlealerts.git```
2. ```cd googlealerts```
3. ```python3 alerts.py```
4. ```python3 alerts.py```

Just run the script twice so it can find the tools it had to install.


![Alt Text](https://i.imgur.com/B4WyfDH.gif)

Right now you should be able to make a discord bot here:
https://discord.com/developers/applications/
Once it is created and added to your server:

If you choose
1. (11) Run Discord Bot
2. 3. Run User interaction mode !news word

As long as all the other menu settings were True, it should start the discord bot and login to the server. Now if you type in on discord:

1. ```!news trump```

It will pull all the latest news articles about Trump.

# Todo
Fix it for when spam requests are made by multiple users. I had a temporary solution which relied on creating a new file called news_collection_in_progress at the start of a request, then deleting it when it was done but it was having issues with being deleted. 
