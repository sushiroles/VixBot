from time import time

def current_unix_time():
	return int(time())

def current_unix_time_ms():
	return int(time() * 1000)