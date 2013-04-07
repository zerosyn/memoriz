#!/usr/bin/python
#encoding=utf-8

import wx
import urllib2
import json
import threading
import functools
from Queue import Queue
from urllib import urlencode

from constant import *

# from pprint import pprint
# import traceback

def async(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		threading.Thread(target=func, args=args, kwargs=kwargs).start()
	return wrapper

class ASyncHTTP:
	def __init__(self, callback):
		self.__status = IDLE
		self.__callback = callback
		self.__queue = Queue()

	def Push(self, key, value):
		self.__queue.put({'key': key, 'value': value})

	def Sync(self, force=False):
		if self.__queue.empty() and not force:
			return
		if self.__status == IDLE:
			self.__status = LOCKED
			task_map = {}
			while not self.__queue.empty():
				task = self.__queue.get()
				if 'key' in task and len(task['key']) > 0:
					task_map[task['key']] = task['value']
			#threading.Thread(target=self.__Run, args=(task_map,)).start()
			self.__Run(task_map)

	@async
	def __Run(self, task_map):
		try:
			params = urlencode({"user": "zero", "task": json.dumps(task_map)})
			# try 3 times
			data = ''
			attempts = 0
			while len(data) == 0 and attempts < 3:
				data = urllib2.urlopen(SERVER, params).read()
				attempts += 1
			if len(data) > 0:
				result_map = json.loads(data)
				wx.CallAfter(self.__callback, result_map)
			else:
				raise Exception
		except Exception, e:
			# print traceback.format_exc()
			print 'sync failed'
		finally:
			self.__status = IDLE
			if not self.__queue.empty():
				self.Sync()