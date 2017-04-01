import discord
import asyncio
import random
import uuid
import yaml

from discord.ext import commands
from youtube_dl.utils import DownloadError


with open('config.yml') as f:
    config = yaml.load(f)

bot = commands.Bot(command_prefix='!ktn ', description='Nyaaaaaaa!')

# Eveto inicializador
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

"""Este evento es para capturar mensajes, necesario para analizar el mensaje
@bot.event
async def on_message(message):

    if message.content.startswith('!ktn saludame'):
        # Saluda al autor del mensaje #
        author = str(message.author).split("#")[0]
        msg = "Hola {}! :3".format(author)
        await bot.send_message(message.channel, msg)

    elif message.content.startswith('!ktn opina'):
        # Opina con una respuesta al azar #
        author = str(message.author).split("#")[0]
        opciones = ["Sí... Es interesante", "Yo no digo nada", "Lolazo", "Ay lmao", "Miau :3", "Nyaaaa :3"]
        msg = random.choice(opciones)
        await client.send_message(message.channel, msg)
  
    elif message.content.startswith('!ktn gatitos'):
        # Muestra imágenes de gatitos # 
        await client.send_message(message.channel, 'http://www.randomkittengenerator.com/cats/rotator.php?'+my_random_string(6))
  
    elif message.content.startswith('!ktn frase'):
        # Muestra una frase célebre aleatoria #
        frase = random_sentence()
        await client.send_message(message.channel, frase)
   
    elif message.content.startswith('!ktn trasciende'):
        # Trasciende #
        await client.send_message(message.channel, "https://www.youtube.com/watch?v=uwmeH6Rnj2E")
   
    elif message.content.startswith('!ktn transformice'):
        # No sé que es esto XD #
        await client.send_message(message.channel, "https://www.youtube.com/watch?v=l4i8BXoa4Z8")
"""

@bot.command()
async def suma(left : int, right : int):
    """Suma dos números"""
    await bot.say(left + right)

@bot.command()
async def dado(dice : str):
    """Tira un dado NxM format."""
    try:
        limit, rolls = map(int, dice.split('x'))
    except Exception:
        await bot.say('El formato del dado debe ser NxM, donde N son el número de caras y M las tiradas!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='Elige una opción de entre varias')
async def elige(*choices : str):
    """Elige entre mútiples posibilidades"""
    await bot.say(random.choice(choices))

@bot.command()
async def joined(member : discord.Member):
    """Anuncia cuando ha entrado alguien"""
    await bot.say('{0.name} ha entrado {0.joined_at}'.format(member))


if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            print(channel)
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Ya estoy en el canal de voz...')
        except discord.InvalidArgument:
            await self.bot.say('Este no es un canal de voz...')
        else:
            await self.bot.say('Estoy listo para reproducir audio en ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        print(summoned_channel)
        if summoned_channel is None:
            await self.bot.say('No estás en un canal de voz')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.35
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def vol(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 1:
                await self.bot.say('Skip vote passed, skipping song...')
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/1]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))

def random_sentence():
    """Returns a formatted random line from a text file"""
    line = random.choice(open(config['frases'], encoding="utf8").readlines())
    parts = line.split('(')
    if len(parts) == 2:
        line = '"{}"\n—{}'.format(parts[0].strip(), parts[1][:-3])
        return line
    else:
        return line

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.


bot.add_cog(Music(bot))
bot.run(config['token'])

