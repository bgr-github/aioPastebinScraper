import aiohttp
import aiofiles
import asyncio
import async_timeout
import os
import time
from bs4 import BeautifulSoup

LOOP_TIME = 10 # In Seconds
TIMEOUT = 30
RUNNING = True
URL = 'https://pastebin.com/'
DIR = 'pastebin_dumps'

# Saves the pastebin URL data into a file
async def save_url(session, href: str):
	raw = 'https://pastebin.com/raw/' + href
	response = await fetch(session, raw)
	file_dir = '{}/{}.txt'.format(DIR, href)
	async with aiofiles.open(file_dir, mode='w') as file:
		try:
			await file.write(response)
			await print('Added: ' + file_dir)
		except UnicodeError:
			pass

# Yields recent pastes from pastebin's homepage
async def get_links(html: str):
	soup = BeautifulSoup(html, 'html.parser')
	for li in soup.find('ul', {'class': 'right_menu'}):
		await asyncio.sleep(1)
		yield li.a.get('href').strip('/')

# Function to fetch the page's HTML
async def fetch(session, url: str):
	try:
		with async_timeout.timeout(TIMEOUT):
			async with session.get(url) as response:
				return await response.text()
	except asyncio.TimeoutError:
		print('Connection timed out after {} seconds.'.format(TIMEOUT))

async def main():
	async with aiohttp.ClientSession() as session:
		html = await fetch(session, URL)
		
		async for href in get_links(html):
			await save_url(session, href)

if __name__ == '__main__':
	# Creates the directory if it doesn't exist.
	if not os.path.exists(DIR):
		os.makedirs(DIR)

	# Asyncio Event Loop
	event_loop = asyncio.get_event_loop()
	try:
		while RUNNING:
			event_loop.run_until_complete(main())
			time.sleep(LOOP_TIME)
	finally:
		event_loop.close()