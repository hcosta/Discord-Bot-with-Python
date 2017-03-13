# Discord-Bot-with-Python
Testing Purposes

## 1. Set up the bot and enter some servers
Documentation here [https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token]

## 2. Install discord.py (with python 3 as default)
*Without voice support*
```
python -m pip install -U discord.py
```

*With voice support*
```
python -m pip install -U discord.py[voice]
```

## 3. Configure token and other profile options in test.py
```
token = ''  # HERE
avatar = './img/kitty.jpg'
nickname = 'Kitten'
```

## 4. Run the bot
```
python test.py
```

## 5. Test commands
* !test: Counts user messages
* !sleep: Sleeps for 5 seconds 
* !info: Shows sample message 
* !setnick: Sets profile username
* !setavatar: Sets profile avatar