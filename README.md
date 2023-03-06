# googlealerts
Manager for Google Alerts

Simply run
1. ```git clone https://github.com/AIMadeScripts/googlealerts.git```
2. ```cd googlealerts```
2a. ```pip install feedparser```
3. ```python3 alerts.py```

In some circumstances, You will need to run the script twice. This is because the script will automatically install the packages it requires itself, but then can't call on them straight away or automatically restart the script. 


![Alt Text](https://i.imgur.com/B4WyfDH.gif)

Right now you should be able to make a discord bot here:
https://discord.com/developers/applications/
Once it is created and added to your server:


Create your feed.txt file using the alerts.py then, you can simply run
```python3 bot.py```

Inside discord now, you can type
```!post_feed```

It will start printing articles to your server from the feed.txt file.

# Todo
Add a menu option in for automating every x hours the user chooses grabbing the feed then piping it into discord.
Also set it up in only one channel rather than any channel and only respond to !post_feed.
