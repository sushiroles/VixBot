import discord as discord 
from discord import app_commands
from discord.ext import tasks

from random import randint
from asyncio import *
from Random.time import *
import configparser

from APIs import *



config = configparser.ConfigParser()
config.read('config.ini')

tokens = configparser.ConfigParser()
tokens.read('tokens.ini')

vars = configparser.ConfigParser()
vars.read('vars.ini')



class Client(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.synced = False
		
intents = discord.Intents.all()
intents.message_content = True
intents.presences = True
intents.members = True
client = Client(intents = intents)
tree = app_commands.CommandTree(client)



@client.event
async def on_ready():
	await client.wait_until_ready()
	if not client.synced:
		await tree.sync()
		client.synced = True
	if not check_for_stream.is_running():
		check_for_stream.start()
	announcements_channel = await client.fetch_channel(int(config['channels']['stream_announcements']))
	await announcements_channel.send('-# (test :3)')



@tasks.loop(seconds = 5)
async def check_for_stream():
	stream_data = await twitch.is_streaming()
	vix_data = await twitch.get_profile()
	announcements_channel = await client.fetch_channel(int(config['channels']['stream_announcements']))
	if stream_data['is_live'] == True and vars['stream_notifs']['is_live'] == 'False':
		embed = discord.Embed(
			title = f'{stream_data['title']}',
			url = "https://twitch.tv/vixrtv",
			colour = 0x6441a5
		)
		embed.set_author(name = f"Vix is live and streaming {stream_data['activity']}!", icon_url = vix_data['profile_image_url'],)
		embed.set_image(url = stream_data['thumbnail_url'].replace('{width}', config['stream_announcements']['tres_w']).replace('{height}', config['stream_announcements']['tres_h']))
		embed.set_footer(text = "~VixrBot :3")

		await announcements_channel.send(f'<@&{config['roles']['stream_notifs_role_id']}>   >>> https://twitch.tv/vixrtv <<<', embed = embed)

		vars.set('stream_notifs', 'is_live', 'True')
		with open('vars.ini', 'w') as vars_file:
			vars.write(vars_file)
	elif stream_data['is_live'] == False and vars['stream_notifs']['is_live'] == 'True':
		vars.set('stream_notifs', 'is_live', 'False')
		with open('vars.ini', 'w') as vars_file:
			vars.write(vars_file)
		


client.run(tokens['discord']['token'])