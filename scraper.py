import aiohttp
import aiofiles
import asyncio
import async_timeout
import argparse
import os
import sys
import time
from bs4 import BeautifulSoup

# Global Constants
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
		except (UnicodeError, TypeError):
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
		sys.exit(0)

async def main():
	# Initiate Connection
	async with aiohttp.ClientSession() as session:
		html = await fetch(session, URL)
		
		try:
			async for href in get_links(html):
				await save_url(session, href)
		except TypeError:
			pass

if __name__ == '__main__':
	# Argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '-timeout', type=int,
						help='Timeout in seconds. Default is 15',
						default=15)
	parser.add_argument('-l', '-loops', type=int,
						help='Loop time in seconds. 10 is default.',
						default=10)

	args = parser.parse_args()

	TIMEOUT = args.t
	LOOP_TIME = args.l

	print('Timeout: {}\nLoop Time: {}'.format(TIMEOUT, LOOP_TIME))

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