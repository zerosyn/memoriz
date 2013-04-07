#!/usr/bin/python
#encoding=utf-8

import wx
#from wx.lib.platebtn import PlateButton
from wx.lib.buttons import GenButton  

from constant import *
from resource import Resource

class FlatButton(GenButton):
	def InitOtherEvents(self):
		self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouse)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouse)

	def OnMouse(self, evt):
		self.Refresh()
		evt.Skip()

	def DrawBezel(self, dc, x1, y1, x2, y2):
		rect = wx.Rect(x1, y1, x2, y2)
		if self.up:
			state = 0
		else:
			state = wx.CONTROL_PRESSED
		if not self.IsEnabled():
			state = wx.CONTROL_DISABLED
		pt = self.ScreenToClient(wx.GetMousePosition())
		if self.GetClientRect().Contains(pt):
			state = wx.CONTROL_CURRENT
		wx.RendererNative.Get().DrawItemSelectionRect(self, dc, rect, state)


class FlatDialog(wx.Dialog):
	def __init__(self, parent, message, pos=False, style=0, btns=[{'label':'OK', 'callback':False, 'default':True}]):
		super(FlatDialog, self).__init__(parent, -1, APP_NAME, style=wx.SIMPLE_BORDER | style)
		
		self.SetBackgroundColour(Resource('color_dark'))
		question = wx.StaticText(self, label=message)
		question.SetFont(Resource('dialog_font'))
		btn_panel = wx.Panel(self, -1)
		btn_panel.SetBackgroundColour(Resource('color_bright'))
		button_list = [self.GenerateButton(btn_panel, btn_cfg) for btn_cfg in btns]

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((20, 0), 1, wx.EXPAND)
		hbox.AddMany([(button, 0, wx.ALL, 5) for button in button_list])
		btn_panel.SetSizer(hbox)
		vbox.Add(question, 0, flag=wx.EXPAND | wx.ALL, border=10)
		vbox.Add(btn_panel, 1, flag=wx.EXPAND | wx.ALL, border=0)
		self.SetSizer(vbox)
		self.Fit()
		if not pos:
			self.CentreOnScreen()
		else:
			self.MoveXY(max(pos.x - self.GetSize().GetWidth() / 2, 0), pos.y)

		self.ShowModal()

	def GenerateButton(self, parent, config):
		#button = PlateButton(btn_panel, label=btn_cfg['label'])
		button = FlatButton(parent, label=config['label'])
		#button.SetUseFocusIndicator(False)
		button.SetBackgroundColour(Resource('color_moderate'))
		button.SetFont(Resource('dialog_font'))
		if 'default' in config and config['default']:
			button.SetFocus()

		callback_list = []
		if 'callback' in config:
			callback_list.append(config['callback'])
		callback_list.append(self.Destroy)
		button.Bind(wx.EVT_BUTTON, lambda e: [func() for func in callback_list])
		return button

class AlertDialog(FlatDialog):
	def __init__(self, parent, message):
		super(AlertDialog, self).__init__(parent, message, style=wx.STAY_ON_TOP, btns=[{'label':u'わかりました'}])

class QuestionDialog(FlatDialog):
	def __init__(self, parent, message, callback, pos=False):
		btns = [
			{'label':u"はい、大丈夫だ", 'callback':callback},
			{'label':u"中止する", 'default':True}
		]
		super(QuestionDialog, self).__init__(parent, message, pos=pos, btns=btns)