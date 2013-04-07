#!/usr/bin/python
#encoding=utf-8

import wx
import uuid

from constant import *
from resource import Resource
from dialog import QuestionDialog
from sync import ASyncHTTP

# from pprint import pprint

class Container(wx.Panel):
	def ReLayout(self):
		self.GetSizer().Layout()
		self.GetParent().GetSizer().Layout()

class Memo(Container):
	def __init__(self, parent, key, text=''):
		super(Memo, self).__init__(parent)
		self.key = key
		self.text = text
		self.lock = False
		self.deleted = False

		self.__static = wx.StaticText(self, label=text)
		self.__editor = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.__editor.Hide()
		self.__del_button = wx.BitmapButton(self, -1, Resource('del_btn'), style=wx.BU_EXACTFIT)
		self.__del_button.SetBitmapHover(Resource('del_btn_hover'))
		# self.__del_button.Hide()

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.AddMany([
			(self.__static, 1, wx.EXPAND),
			(self.__editor, 1, wx.EXPAND),
			(self.__del_button)
		])
		self.SetSizer(hbox)
		self.ReLayout()

		self.__static.Bind(wx.EVT_LEFT_DCLICK, self.OnEdit)
		self.__del_button.Bind(wx.EVT_BUTTON, self.OnDelete)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSubmit, self.__editor)

		# self.Bind(wx.EVT_MOTION, self.OnHover)
		# self.Bind(wx.EVT_LEAVE_WINDOW, self.OnBlur)

	def OnHover(self, e):
		self.__del_button.Show()
		self.ReLayout()

	def OnBlur(self, e):
		self.__del_button.Hide()
		self.ReLayout()

	def OnEdit(self, e):
		if not self.lock:
			self.GetParent().FinishEditAll()
			self.lock = True
			self.__editor.SetValue(self.text)
			self.__editor.SelectAll()
			self.__static.Hide()
			self.__editor.Show()
			self.ReLayout()
			self.__editor.SetFocus()

	def OnSubmit(self, e):
		if self.FinishEdit():
			self.Sync(self.text)

	def FinishEdit(self):
		if self.lock:
			old_value = self.text
			self.text = self.__editor.GetValue().strip()
			self.__static.SetLabel(self.text)
			self.__editor.Hide()
			self.__static.Show()
			self.ReLayout()
			self.lock = False
			return old_value != self.text
		return False
		

	def OnDelete(self, e):
		# under the delete button
		pos = self.__del_button.GetScreenPosition() + wx.Point(0, self.__del_button.GetSize().GetHeight())
		QuestionDialog(self, u'本当に削除しますか？', callback=self.Delete, pos=pos)
		# ret  = wx.MessageBox('Are you sure to delete?', 'Question', wx.YES_NO | wx.NO_DEFAULT)
		# if ret == wx.YES:
		# 	self.lock = False
		# 	self.deleted = True
		# 	self.Hide()
		# 	self.ReLayout()
		# 	self.Sync(False)

	def Delete(self):
		if not self.deleted:
			self.lock = False
			self.deleted = True
			self.Hide()
			self.ReLayout()
			self.Sync(False)

	def Sync(self, text):
		self.GetParent().Sync(self.key, text)

	def SyncCallback(self, text):
		if not self.lock:
			if text == False:
				self.deleted = True
				self.Hide()
				self.ReLayout()
			else:
				self.text = text
				self.__static.SetLabel(self.text)
				self.ReLayout()


class MemoList(Container):
	def __init__(self, parent):
		super(MemoList, self).__init__(parent)
		self.__list = {}
		self.synchronizer = ASyncHTTP(self.SyncCallback)

		vbox = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(vbox)

		# for alarm
		# self.__timer = wx.Timer(self)
		# self.__timer.Start(milliseconds=600000)
		# self.Bind(wx.EVT_TIMER, self.__OnTimer, self.__timer)

	def Add(self, text, key=False, sync=True):
		if key == False:
			key = unicode(str(uuid.uuid4()))
		new_memo = Memo(self, key, text)
		self.__list[key] = new_memo
		self.GetSizer().Add(new_memo, flag=wx.EXPAND)
		self.ReLayout()
		if sync:
			self.Sync(key, text)

	def Del(self, key):
		if key in self.__list:
			memo = self.__list[key]
			if memo.deleted:
				del self.__list[key]
				memo.Destroy()
				self.ReLayout()

	def FinishEditAll(self, e=False):
		for key in self.__list:
			if self.__list[key].FinishEdit():
				self.synchronizer.Push(key, self.__list[key].text)
		self.synchronizer.Sync()

	def Sync(self, key, text):
		self.synchronizer.Push(key, text)
		self.synchronizer.Sync()

	def SyncAll(self):
		self.synchronizer.Sync(force=True)

	def SyncCallback(self, result_map):
		print 'sync success'
		remove_keys = []
		for key in self.__list:
			if key in result_map:
				self.__list[key].SyncCallback(result_map[key])
				del result_map[key]
			else:
				remove_keys.append(key)
		for key in result_map:
			self.Add(result_map[key], key, sync=False)
		for key in remove_keys:
			self.Del(key)
