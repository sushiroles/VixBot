from Random.time import *
from Random.json_tools import *

from APIs.credentials import credentials

import aiohttp
from asyncio import run

class Twitch:
	def __init__(self, client_id: str = credentials['twitch']['client_id'], client_secret: str = credentials['twitch']['client_secret']):
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_expiration_date = None

		run(self.get_token())

	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_unix_time() > self.token_expiration_date):
			async with aiohttp.ClientSession() as session:
				#request = 'get_token'
				api_url = 'https://id.twitch.tv/oauth2/token'
				api_data = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
				api_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

				async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
					if response.status == 200:
						json_response = await response.json()
						self.token = json_response['access_token']
						self.token_expiration_date = current_unix_time() + int(json_response['expires_in'])
					
					# else:
					# 	error = Error(
					# 		service = self.service,
					# 		component = self.component,
					# 		http_code = response.status,
					# 		error_msg = 'HTTP error when getting token',
					# 		request = {'request': request}
					# 	)
					# 	await log(error)
					# 	return error

		return self.token



	async def get_profile(self):
		async with aiohttp.ClientSession() as session:
			api_url = f'https://api.twitch.tv/helix/users'
			api_params = {
				'login': credentials['twitch']['user']
			}
			api_headers = {
				'Authorization': f'Bearer {await self.get_token()}',
				'Client-Id': self.client_id
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, headers = api_headers, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					json = await response.json()
					json = json['data'][0]
					return {
						'id': json['id'],
						'login': json['login'],
						'display_name': json['display_name'],
						'type': json['type'],
						'broadcaster_type': json['broadcaster_type'],
						'description': json['description'],
						'profile_image_url': json['profile_image_url'],
						'offline_image_url': json['offline_image_url'],
						'created_at': json['created_at']
					}
	


	async def is_streaming(self):
		async with aiohttp.ClientSession() as session:
			api_url = f'https://api.twitch.tv/helix/streams'
			api_params = {
				'user_login': credentials['twitch']['user']
			}
			api_headers = {
				'Authorization': f'Bearer {await self.get_token()}',
				'Client-Id': self.client_id
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, headers = api_headers, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					json = await response.json()
					if json['data'] != []:
						json = json['data'][0]
						return {
							'is_live': True,
							'title': json['title'],
							'activity': json['game_name'],
							'thumbnail_url': json['thumbnail_url'],
							'viewer_count': json['viewer_count']
						}
					else:
						return {
							'is_live': False
						}