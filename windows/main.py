#!/usr/bin/python
#encoding=utf-8

import wx
import win32con #for the VK keycodes

from constant import *
from resource import Resource
from memo import MemoList
from dialog import *

def CreateMenuItem(menu, label, func):
	item = wx.MenuItem(menu, -1, label)
	menu.Bind(wx.EVT_MENU, func, id=item.GetId())
	menu.AppendItem(item)
	return item

# static variable hotkey_counter
def BindGlobalHotkey(window, modifier, key, func, hotkey_counter=[]):
	if len(hotkey_counter) == 0:
		hotkey_counter.append(0)
	hotkey_counter[0] += 1
	window.RegisterHotKey(hotkey_counter[0], modifier, key)
	window.Bind(wx.EVT_HOTKEY, func, id=hotkey_counter[0])

class Window(wx.Frame):
	def __init__(self, parent):
		super(Window, self).__init__(parent, title=APP_NAME)
		# self.SetWindowStyleFlag(wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.InitUI()
		self.__memo_list.SyncAll()
		
	def InitUI(self):
		panel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)

		self.__new_memo = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		self.__memo_list = MemoList(panel)

		vbox.Add(self.__new_memo, flag=wx.EXPAND | wx.ALL, border=4)
		vbox.Add(self.__memo_list, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)
		panel.SetSizer(vbox)

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		BindGlobalHotkey(self, win32con.MOD_SHIFT | win32con.MOD_CONTROL, ord('D'), self.OnGlobalHotkey)

		self.Bind(wx.EVT_TEXT_ENTER, self.OnAddMemo, self.__new_memo)
		self.__new_memo.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		panel.Bind(wx.EVT_LEFT_UP, self.__memo_list.FinishEditAll)

	def OnAddMemo(self, e):
		text = self.__new_memo.GetValue().strip()
		self.__new_memo.Clear()
		if len(text) > 0:
			self.__memo_list.Add(text)

	def OnKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.Hide()
		elif key == wx.WXK_F5:
			self.__memo_list.SyncAll()
		e.Skip()

	def OnClose(self, e):
		self.Hide()
		e.Veto()

	def OnGlobalHotkey(self, e):
		self.Toggle()

	def Toggle(self):
		if not self.IsShown() or self.IsIconized():
			self.Show()
			self.Raise()
			self.Iconize(False)
			self.__new_memo.SetFocus()
		else:
			self.Hide()


class TaskBarIcon(wx.TaskBarIcon):
	def __init__(self):
		super(TaskBarIcon, self).__init__()
		icon = Resource('icon')
		self.SetIcon(icon, APP_NAME)

		self.window = Window(None)
		self.window.Toggle()

		self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.OnLeftDown)
		# for test
		BindGlobalHotkey(self.window, win32con.MOD_SHIFT | win32con.MOD_CONTROL, ord('X'), self.OnMenuExit)

		self.info_box = wx.AboutDialogInfo()
		self.info_box.SetIcon(icon)
		self.info_box.SetName(APP_NAME)
		self.info_box.SetVersion('0.1')
		self.info_box.SetDescription('Memorize clips everywhere')
		self.info_box.SetCopyright(u'©Zero 2012')
		self.info_box.SetWebSite('http://memoriz.co.cc')

	def CreatePopupMenu(self):
		menu = wx.Menu()
		CreateMenuItem(menu, 'About', self.OnMenuAbout)
		menu.AppendSeparator()
		CreateMenuItem(menu, 'Exit', self.OnMenuExit)
		return menu

	def OnLeftDown(self, event):
		self.window.Toggle()

	def OnMenuAbout(self, event):
		wx.AboutBox(self.info_box)

	def OnMenuExit(self, event):
		self.window.Destroy()
		wx.CallAfter(self.Destroy)

def main():
	app = wx.PySimpleApp()
	TaskBarIcon()
	app.MainLoop()

if __name__ == '__main__':
	main()