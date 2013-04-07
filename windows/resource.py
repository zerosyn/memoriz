#!/usr/bin/python
#encoding=utf-8

import wx

def Resource(key, data={}):
	if len(data) == 0:
		data = dict(
			color_dark = wx.Colour(160, 170, 180),
			color_moderate = wx.Colour(180, 190, 200),
			color_bright = wx.Colour(200, 210, 220),
			dialog_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, face=u'微软雅黑'),
			icon = wx.IconFromBitmap(wx.Bitmap('icon.png')),#wx.Icon('icon.png', wx.BITMAP_TYPE_PNG))
			del_btn = wx.Image("del.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
			del_btn_hover = wx.Image("del_hover.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		)
	if key in data:
		return data[key]
	else:
		return False