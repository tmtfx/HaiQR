#!/boot/system/bin/python

#   A Simple QR generator for Haiku.
#   Copyright (C) 2021  Fabio Tomat
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

import os,sys,struct,tempfile

jes=False
try:
	import BApplication,SupportKit
	from BStringItem import BStringItem
#	from BListView import BListView
#	from BScrollView import BScrollView
	from BWindow import BWindow
	from BMessage import BMessage
	from BMenuItem import BMenuItem
	from BMenu import BMenu
	from BBox import BBox
	from BButton import BButton
	from BMenuBar import BMenuBar
	from BPopUpMenu import BPopUpMenu
	from BSeparatorItem import BSeparatorItem
	from BStringView import BStringView
#	from BSlider import BSlider
	from BTextView import BTextView
	from BFont import be_plain_font, be_bold_font
	from BTextControl import BTextControl
	from BAlert import BAlert
#	from BListItem import BListItem
#	from BStatusBar import BStatusBar
	from StorageKit import *
	from BTranslationUtils import *
	from BFile import BFile
	from BBitmap import BBitmap
#	from BCheckBox import BCheckBox
	from BView import BView
	import BFilePanel, BEntry
	from InterfaceKit import B_VERTICAL,B_FOLLOW_ALL,B_FOLLOW_TOP,B_FOLLOW_LEFT,B_FOLLOW_RIGHT,B_TRIANGLE_THUMB,B_BLOCK_THUMB,B_FLOATING_WINDOW,B_TITLED_WINDOW,B_WILL_DRAW,B_NAVIGABLE,B_FRAME_EVENTS,B_ALIGN_CENTER,B_FOLLOW_ALL_SIDES,B_MODAL_WINDOW,B_FOLLOW_TOP_BOTTOM,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT_RIGHT,B_SINGLE_SELECTION_LIST,B_NOT_RESIZABLE,B_NOT_ZOOMABLE,B_PLAIN_BORDER,B_FANCY_BORDER,B_NO_BORDER,B_ITEMS_IN_COLUMN,B_ENTER
	from AppKit import B_QUIT_REQUESTED,B_KEY_UP,B_KEY_DOWN,B_MODIFIERS_CHANGED,B_UNMAPPED_KEY_DOWN,B_REFS_RECEIVED,B_SAVE_REQUESTED,B_CANCEL
	from StorageKit import B_SAVE_PANEL,B_FILE_NODE
	from SupportKit import B_ERROR
except:
	print "your system lacks of Bethon modules"
	jes = True
	
try:
	from backports import tempfile
except:
	print "your python environment lacks of backports.tempfile"
	jes = True
	
try:
	import qrcode
except:
	print "your python environment lacks of qrcode module"
	jes = True
try:
	from PIL import Image
except:
	print "your python environment lacks of pillow module"
	jes = True

if jes:
	sys.exit(1)

class PView(BView):
	def __init__(self,frame,name,immagine):
		self.immagine=immagine
		self.frame=frame
		BView.__init__(self,self.frame,name,B_FOLLOW_ALL_SIDES,B_WILL_DRAW)
		
	def UpdateImg(self,immagine):
		self.immagine=immagine
		a,b,c,d=self.frame
		rect=(0,0,c-a,d-b)
		self.DrawBitmap(self.immagine,rect)

	def Draw(self,rect):
		BView.Draw(self,rect)
		a,b,c,d=self.frame
		rect=(0,0,c-a,d-b)
		self.DrawBitmap(self.immagine,rect)
		
class HaiQRWindow(BWindow):
	Menus = (
		('File', ((1, 'Generate QR'),(2, 'Save QR'),(5, 'Add Logo'),(None, None),(B_QUIT_REQUESTED, 'Quit'))),
		('Help', ((4, 'Help'),(3, 'About')))
		)
		
	def __init__(self, frame):
		selectionmenu=0
		BWindow.__init__(self, frame, 'QR generator for Haiku!', B_TITLED_WINDOW, B_WILL_DRAW)
		bounds = self.Bounds()
		self.bar = BMenuBar(bounds, 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		for menu, items in self.Menus:
			menu = BMenu(menu)
			for k, name in items:
				if k is None:
						menu.AddItem(BSeparatorItem())
				else:
						msg = BMessage(k)
						menu.AddItem(BMenuItem(name, msg))
			self.bar.AddItem(menu)
		l, t, r, b = bounds
		self.AddChild(self.bar)
		##### COLOR GRAY UNDER LISTS
		self.underlist = BBox((l, t + barheight, r, b), 'underlist', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underlist)
		##### PLACE TO PUT TEXT FOR QR GENERATOR #####
		self.Hintlabel= BStringView((l+7,b-barheight-40,70,b-barheight-10),"Label","Paste here:",B_FOLLOW_LEFT | B_FOLLOW_BOTTOM)
		self.underlist.AddChild(self.Hintlabel)
		self.tachetest=BTextControl((73,b-barheight-30,r-57,b-barheight-12),'TxTView', None,None,BMessage(1),B_FOLLOW_LEFT_RIGHT | B_FOLLOW_BOTTOM)
		self.underlist.AddChild(self.tachetest)
		self.tachetest.MakeFocus(1)
#		self.BUTTON_MSG = struct.unpack('!l', 'PRES')[0]
		self.QRButton = BButton((r-53, b-barheight-32, r-5, b-barheight-10), "QRit", "QR it!", BMessage(1), B_FOLLOW_RIGHT | B_FOLLOW_BOTTOM)
		self.underlist.AddChild(self.QRButton)
		self.qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=10,border=4)
		#zonte pview
		self.qrframe=PView((l+15,t+15,r-15,b-70),"photoframe",None)
		self.underlist.AddChild(self.qrframe)
		#self.imginmemory = False  #boolean that enables "save to disk" function
		self.fp=BFilePanel.BFilePanel(B_SAVE_PANEL)
		self.fp.SetPanelDirectory("/boot/home/Desktop")
		self.fp.SetSaveText("prova.png")
		self.ofp=BFilePanel.BFilePanel()
		self.logopath = ""
		self.qrcreated = False
		self.CanOpenPanel=True


		
# MESSAGES 
	def MessageReceived(self, msg):
		if msg.what == 1:
			#Gjenere QR
			if self.tachetest.Text() != "":
				self.imginmemory = True
				self.qr.clear()
				self.qr.add_data(self.tachetest.Text())
				self.qr.make(fit=True)
				self.qrimg=self.qr.make_image(fill_color="black",back_color="white").convert('RGB')
				if self.logopath != "":
					logo_display = Image.open(self.logopath)
					logo_display.thumbnail((60, 60))
					logo_pos = ((self.qrimg.size[0] - logo_display.size[0]) // 2, (self.qrimg.size[1] - logo_display.size[1]) // 2)
					self.qrimg.paste(logo_display, logo_pos)
				with tempfile.TemporaryDirectory() as temp_dir:
					link=temp_dir+"/tmp.png"
					self.qrimg.save(link)
					self.img=BTranslationUtils.GetBitmap(link)
					self.qrframe.UpdateImg(self.img)
					self.qrcreated = True

			return
		if msg.what == 2:
			#SaveFilePanel
			if self.qrcreated:
				self.CanOpenPanel=False
				self.fp.Show()

		if msg.what == 54173:
			txt=self.fp.GetPanelDirectory()
			savepath= BEntry.BEntry(txt,True).GetPath().Path()
			e = msg.FindString("name")
			completepath = savepath +"/"+ e
			self.qrimg.save(completepath)

		if msg.what == 3:
			#ABOUT
			self.About = AboutWindow()
			self.About.Show()
			return
			
		if msg.what == 4:
			if self.qrcreated:
				BApplication.be_app.WindowAt(0).PostMessage(BMessage(1))
			return
				
		if msg.what == 5:
			if not(self.ofp.IsShowing()):
			#ADD OR REMOVE LOGO
				if self.bar.FindItem("Add Logo").IsMarked():
					#remove logo
					self.logopath=""
					self.bar.FindItem("Add Logo").SetMarked(0)
					BApplication.be_app.PostMessage(BMessage(311))
					if self.qrcreated:
						BApplication.be_app.WindowAt(0).PostMessage(BMessage(1))
				else:
					if self.CanOpenPanel:
						#add logo
						self.bar.FindItem("Add Logo").SetMarked(1)
						self.ofp.Show()
						self.CanOpenPanel=False
			return

		if msg.what == 6:
			self.CanOpenPanel=True
			
		if msg.what == 112:
			self.logopath = msg.FindString("path=")
			return

		BWindow.MessageReceived(self, msg)
		

	def QuitRequested(self):
		print "So long and thanks for all the fish"
		BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
		#BApplication.be_app.WindowAt(0).PostMessage(B_QUIT_REQUESTED)
		return 1

		
class AboutWindow(BWindow):
	kWindowFrame = (150, 150, 650, 620)
	kButtonFrame = (395, 425, 490, 460)
	kWindowName = "About"
	kButtonName = "Close"
	BUTTON_MSG = struct.unpack('!l', 'PRES')[0]

	def __init__(self):							
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_MODAL_WINDOW, B_NOT_RESIZABLE|B_WILL_DRAW)
		bbox=BBox((0,0,500,470), 'underbox', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(bbox)
		self.CloseButton = BButton(self.kButtonFrame, self.kButtonName, self.kButtonName, BMessage(self.BUTTON_MSG))		
		cise=(10,4,490,420)
		cjamput=(0,0,480,420)
		self.messagjio= BTextView(cise, 'TxTView', cjamput, B_FOLLOW_ALL, B_WILL_DRAW)
		self.messagjio.SetStylable(1)
		self.messagjio.MakeSelectable(0)
		self.messagjio.MakeEditable(0)
		stuff = '\n\t\t\t\t\t\t\t\tHaiQR\n\n\t\t\t\t\t\t\t\t\t\t\tA simple QR generator\n\t\t\t\t\t\t\t\t\t\t\tfor Haiku, version 0.1\n\t\t\t\t\t\t\t\t\t\t\tcodename "Cure"\n\n\t\t\t\t\t\t\t\t\t\t\tby Fabio Tomat aka TmTFx\n\t\t\t\t\t\t\t\t\t\t\te-mail:\n\t\t\t\t\t\t\t\t\t\t\tf.t.public@gmail.com\n\n\n\n\nGNU GENERAL PUBLIC LICENSE:\nThis program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program.  If not, see \n<http://www.gnu.org/licenses/>'
		n = stuff.find('HaiQR')
		m = stuff.find('This')
		self.messagjio.SetText(stuff, [(0, be_plain_font, (0, 0, 0, 0)), (n, be_bold_font, (0, 150, 0, 0)), (n + 5, be_plain_font, (0, 0, 0, 0)),(m,be_plain_font,(100,150,0,0))])
		bbox.AddChild(self.messagjio)
		bbox.AddChild(self.CloseButton)
		self.CloseButton.MakeFocus(1)
		link=sys.path[0]+"/data/HaiQR.png"
		self.img=BTranslationUtils.GetBitmap(link)
		self.photoframe=PView((40,40,255,255),"photoframe",self.img)
		bbox.AddChild(self.photoframe)

	def MessageReceived(self, msg):
		if msg.what == self.BUTTON_MSG:
			self.Quit()
		else:
			return
		
		
class HaiQRApplication(BApplication.BApplication):

	def __init__(self):
		BApplication.BApplication.__init__(self, "application/x-vnd.HaiQR")
		self.txtpath=""

	def ReadyToRun(self):
		window((100,80,600,600))
# REF MESSAGES OpenFilePanel		
	def RefsReceived(self, msg):
		#msg.PrintToStream()
		if msg.what == B_REFS_RECEIVED:
			i = 0
			while 1:
				try:
					e = msg.FindRef("refs", i)
					bpatho= BEntry.BEntry(e,True).GetPath()
					self.txtpath= bpatho.Path()
					a=BMessage(112)
					a.AddString("path=",self.txtpath)
					BApplication.be_app.WindowAt(0).PostMessage(a)
				except:
					e = None
				if e is None:
					break
				i = i + 1
				
	def MessageReceived(self, msg):
		if msg.what == B_SAVE_REQUESTED:
			e = msg.FindString("name")
			messaggio = BMessage(54173)
			messaggio.AddString("name",e)
			BApplication.be_app.WindowAt(0).PostMessage(messaggio)
			return
			
		if msg.what == B_CANCEL:
			if self.txtpath=="":
				#se nissun file di salvaa
				BApplication.be_app.WindowAt(0).PostMessage(BMessage(5))
				BApplication.be_app.WindowAt(0).PostMessage(BMessage(6))
			else:
				#se file viert inzorne imagjin
				BApplication.be_app.WindowAt(0).PostMessage(BMessage(4))
				BApplication.be_app.WindowAt(0).PostMessage(BMessage(6))
			return
			
		if msg.what == 311:
			self.txtpath = ""
			return
			
	def QuitRequested(self):
		return 1
		
		
def window(rectangle):
	window = HaiQRWindow(rectangle)
	window.Show()		
		
		
HaiQR = HaiQRApplication()
HaiQR.Run()
		
