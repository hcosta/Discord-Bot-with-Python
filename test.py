import discord
import asyncio

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
  
    # Sample testing
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))

    # Sample testing sleep 5 seconds
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

    # Set avatar (https://discordapp.com/developers/docs/resources/user)
    elif message.content.startswith('!setavatar'):
        with open('./img/kitty.jpg', 'rb') as f:
            await client.edit_profile(avatar=f.read())

    # Set nickname (https://discordapp.com/developers/docs/resources/user)
    elif message.content.startswith('!setnick'):
        await client.edit_profile(username="Kitten")

    # Show info
    elif message.content.startswith('!info'):
        await client.send_message(message.channel, 
            ':inbox_tray: Yes! :smile: :wave:\n:outbox_tray: No! :smile: :wave:')     

# This token is just for testing right now, will delete in future
client.run('')