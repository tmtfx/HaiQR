#!/boot/system/bin/python3
jes=False
try:
	from Be import BApplication, BWindow, BBox, BRect, BTextControl, BView, BMenu, BMenuBar, BMenuItem, BSeparatorItem, AppDefs, BFont
	from Be import BMessage, BBitmap, BTextView, BButton, BStringItem, window_type, B_NOT_RESIZABLE, B_QUIT_ON_WINDOW_CLOSE, B_CLOSE_ON_ESCAPE
	from Be import BStringView, BMimeType, BPoint, BAlert,BPath,InterfaceDefs,BScreen
	from Be.View import *
	from Be.FindDirectory import *
	from Be.GraphicsDefs import *
	from Be.Alert import alert_type
	from Be.AppDefs import *
	from Be.View import *#B_WILL_DRAW,B_FOLLOW_NONE,B_FOLLOW_ALL_SIDES,B_FOLLOW_ALL,B_NAVIGABLE,B_FOLLOW_LEFT,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT_RIGHT,B_FOLLOW_RIGHT,B_FULL_UPDATE_ON_RESIZE
	from Be.FilePanel import *
	from Be.Font import be_plain_font, be_bold_font
	from Be.InterfaceDefs import border_style

	from Be import BEntry,BUrl,BTranslationUtils
	from Be.Entry import entry_ref
	from Be.Entry import get_ref_for_path
except:
	print("error loading Haiku-PyAPI modules")
	jes = True

import tempfile, os, sys, struct
from threading import Thread

try:
	import qrcode
except:
	jes = True
	print("Install qrcode python module: pkgman install qrcode_python310")

try:
	from PIL import Image
except:
	print("Install Pillow python module: pkgman install pillow_python310\nor pkgman install pillow_x86_python310 according to your architecture")
	jes = True



def openlink(link):
	osd=BUrl(link)
	retu=osd.OpenWithPreferredApplication()

########### TODO INTEGRARE PERCORSI DI INSTALLAZIONE
pothpath=os.path.join(sys.path[0],'data/index.html')
if os.path.exists(pothpath):
	if jes:
		t = Thread(target=openlink,args=(pothpath,))
		t.run()
############################################################################

class PView(BView):
	def __init__(self,frame,name,immagine):
		self.immagine=immagine
		self.frame=frame
		BView.__init__(self,frame,name,8, 20000000)#4660, 2000000|8000000)
		self.SetFlags(B_WILL_DRAW)
		self.SetResizingMode(B_FOLLOW_ALL_SIDES)
		
	def UpdateImg(self,immagine):
		self.Draw(self.Bounds())
		self.immagine=immagine
		rect=BRect(0,0,self.Bounds().Width(),self.Bounds().Height())
		self.DrawBitmap(self.immagine,rect)
	def Refresh(self):
		self.Draw(self.Bounds())
		rect=BRect(0,0,self.Bounds().Width(),self.Bounds().Height())
		self.DrawBitmap(self.immagine,rect)

	def Draw(self,rect):
		BView.Draw(self,rect)
		#rect=BRect(0,0,self.frame.Width(),self.frame.Height())
		rect=BRect(0,0,self.Bounds().Width(),self.Bounds().Height())
		self.DrawBitmap(self.immagine,rect)


class AboutWindow(BWindow):
	def __init__(self):
		scr=BScreen()
		scrfrm=scr.Frame()
		x=(scrfrm.right+1)/2-550/2
		y=(scrfrm.bottom+1)/2-625/2
		BWindow.__init__(self, BRect(x, y, x+550, y+625),"About",window_type.B_MODAL_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		self.bckgnd = BView(self.Bounds(), "backgroundView", 8, 20000000)
		self.bckgnd.SetResizingMode(B_FOLLOW_V_CENTER|B_FOLLOW_H_CENTER)
		bckgnd_bounds=self.bckgnd.Bounds()
		self.AddChild(self.bckgnd,None)
		self.box = BBox(bckgnd_bounds,"Underbox",0x0202|0x0404,border_style.B_FANCY_BORDER)
		self.bckgnd.AddChild(self.box,None)
		################## PBOX ###############################
		pbox_rect=BRect(0,0,self.box.Bounds().Width(),241)
		perc=BPath()
		find_directory(directory_which.B_SYSTEM_DATA_DIRECTORY,perc,False,None)
		ent=BEntry(perc.Path()+"/HaiQR2/FeedGator1c.png")
		if ent.Exists():
			#use mascot installed in system data folder
			ent.GetPath(perc)
			img1=BTranslationUtils.GetBitmap(perc.Path(),None)
			self.pbox=PBox(pbox_rect,"PictureBox",img1)
			self.box.AddChild(self.pbox,None)
		else:
			find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
			ent=BEntry(perc.Path()+"/HaiQR2/Data/FeedGator1c.png")
			if ent.Exists():
				#use mascot installed in user data folder
				ent.GetPath(perc)
				img1=BTranslationUtils.GetBitmap(perc.Path(),None)
				self.pbox=PBox(pbox_rect,"PictureBox",img1)
				self.box.AddChild(self.pbox,None)
			else:
				cwd = os.getcwd()
				ent=BEntry(cwd+"/Data/FeedGator1c.png")
				if ent.Exists():
					#use mascot downloaded with git
					ent.GetPath(perc)
					img1=BTranslationUtils.GetBitmap(perc.Path(),None)
					self.pbox=PBox(pbox_rect,"PictureBox",img1)
					self.box.AddChild(self.pbox,None)
				else:
					print("no mascot found")
		#######################################################
		abrect=BRect(2,242, self.box.Bounds().Width()-2,self.box.Bounds().Height()-2)
		inner_ab=BRect(4,4,abrect.Width()-4,abrect.Height()-4)
		mycolor=rgb_color()
		mycolor.red=0
		mycolor.green=200
		mycolor.blue=0
		mycolor.alpha=0
		self.AboutText = BTextView(abrect, 'aBOUTTxTView', inner_ab , B_FOLLOW_NONE)
		self.AboutText.MakeEditable(False)
		self.AboutText.MakeSelectable(False)
		self.AboutText.SetStylable(True)
		stuff="\nHaiQR2 v2.0\t-\tA simple QR generator for Haiku\n\nThis is a simple QR generator written in Python 3.10 + Haiku-PyAPI and qrcode module\n\nHaiQR2 is a reworked update of HaiQR which used python2 and Bethon.\n\nThis is a beta version, due to ongoing refinements done to Haiku-PyAPI\n\t\t\t\t\t\t\t\t\tdesigned by TmTFx\n\n\t\tpress ESC to close this window"
		self.AboutText.SetFontAndColor(be_bold_font,B_FONT_ALL,mycolor)
		self.AboutText.SetText(stuff,None)
		self.box.AddChild(self.AboutText,None)


class HaiQRWindow(BWindow):
	Menus = (
		('File', ((1, 'Generate QR'),(2, 'Save QR'),(5, 'Add Logo'),(None, None),(AppDefs.B_QUIT_REQUESTED, 'Quit'))),
		('Help', ((8, 'Help'),(3, 'About')))
		)
		
	def __init__(self, frame):
		selectionmenu=0
		BWindow.__init__(self, frame, 'QR generator for Haiku', window_type.B_TITLED_WINDOW,B_QUIT_ON_WINDOW_CLOSE)#|B_CLOSE_ON_ESCAPE)
		bounds = self.Bounds()
		self.bckgnd = BView(bounds, "background",8, 20000000)#B_FOLLOW_NONE,1048576)# B_FOLLOW_ALL_SIDES, 2000000|8000000) less than this value 1048576 you get white background
		#self.bckgnd.SetResizingMode(B_FOLLOW_ALL_SIDES)
		self.bar = BMenuBar(self.bckgnd.Bounds(), 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		for menu, items in self.Menus:
			menu = BMenu(menu)
			for k, name in items:
				if k is None:
						menu.AddItem(BSeparatorItem())
				else:
						menu.AddItem(BMenuItem(name, BMessage(k), name[1],0))
			self.bar.AddItem(menu)
		self.bckgnd.AddChild(self.bar,None)
		self.AddChild(self.bckgnd,None)
		##### COLOR GRAY UNDER LISTS
		self.underlist = BBox(BRect(0, barheight, bounds.Width(), bounds.Height()), 'underlist',0x0202|0x0404,border_style.B_FANCY_BORDER)#, B_FOLLOW_ALL, 2000000|B_NAVIGABLE, border_style.B_FANCY_BORDER) #B_FULL_UPDATE_ON_RESIZE|
		underbounds=self.underlist.Bounds()
		#self.underlist.SetResizingMode(B_FOLLOW_ALL_SIDES)
		self.bckgnd.AddChild(self.underlist,None)
		a=BFont()
		wid=a.StringWidth("Paste here:")
		whereplace=BRect(30,underbounds.Height()-barheight-30,30+wid,underbounds.Height()-barheight-10)
		self.Hintlabel= BStringView(whereplace,"Label","Paste here:")
		##### this is a workaround####
		self.underlist.AddChild(self.Hintlabel,None)
		self.Hintlabel.Hide()
		######## end of workaround ##########################
		self.tachetest=BTextControl(BRect(7,underbounds.Height()-barheight-27,underbounds.Width()-57,underbounds.Height()-barheight-17),'TxTView', 'Paste here:',None,BMessage(1),B_FOLLOW_LEFT_RIGHT | B_FOLLOW_BOTTOM)
		self.tachetest.SetDivider(wid+5)
		self.underlist.AddChild(self.tachetest,None)
		self.tachetest.MakeFocus(1)
		#self.BUTTON_MSG = struct.unpack('!l', 'PRES')[0]
		self.QRButton = BButton(BRect(underbounds.Width()-53, underbounds.Height()-barheight-32, underbounds.Width()-5, underbounds.Height()-barheight-10), "QRit", "QR it!", BMessage(1), B_FOLLOW_RIGHT | B_FOLLOW_BOTTOM)
		self.underlist.AddChild(self.QRButton, None)
		self.qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=10,border=4)
		###### PLACE FOR GENERATED QRs
		self.qrframe=PView(BRect(30,30,underbounds.Width()-30,underbounds.Height()-85),"photoframe",None)
		self.underlist.AddChild(self.qrframe,None)
		###### SAVE PANEL
		#print(int(B_SAVE_PANEL))
		self.fp=BFilePanel(B_SAVE_PANEL,None,None,0,False, None, None, True, True)#B_SAVE_PANEL)
		self.fp.SetPanelDirectory("/boot/home/Desktop")
		self.fp.SetSaveText("prova.png")
		###### OPEN PANEL
		self.ofp=BFilePanel(B_OPEN_PANEL,None,None,0,False, None, None, True, True)
		###### VARIABLES
		self.logopath = ""
		self.qrcreated = False
		self.CanOpenPanel=True
		

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
					self.img=BTranslationUtils.GetBitmap(link,None)
					self.qrframe.UpdateImg(self.img)
					self.qrcreated = True
			return
			
		if msg.what == 2:
			#SaveFilePanel
			if self.qrcreated:
				self.CanOpenPanel=False
				self.fp.Show()
				#be_app.PostMessage(BMessage(11))
			return

		if msg.what == 54173:
			#Save qr
			b=entry_ref()
			self.fp.GetPanelDirectory(b)
			c=BEntry(b)
			d=BPath()
			c.GetPath(d)
			savepath=d.Path()
			e = msg.FindString("name")
			completepath = savepath +"/"+ e
			self.qrimg.save(completepath)
			return

		if msg.what == 3:
			#ABOUT
			self.About = AboutWindow()
			self.About.Show()
			return
			
		if msg.what == 4:
			if self.qrcreated:
				be_app.WindowAt(0).PostMessage(BMessage(1))
			return
				
		if msg.what == 5:
			if not(self.ofp.IsShowing()):
			#ADD OR REMOVE LOGO
				if self.bar.FindItem("Add Logo").IsMarked():
					#remove logo
					self.logopath=""
					self.bar.FindItem("Add Logo").SetMarked(0)
					be_app.PostMessage(BMessage(311))
					if self.qrcreated:
						be_app.WindowAt(0).PostMessage(BMessage(1))
				else:
					if self.CanOpenPanel:
						#add logo
						self.bar.FindItem("Add Logo").SetMarked(1)
						self.ofp.Show()
						self.CanOpenPanel=False
			return

		if msg.what == 6:
			self.CanOpenPanel=True
			return
			
		if msg.what == 112:
			self.logopath = msg.FindString("path=")
			return
			
		if msg.what == 8:
			#HELP
			perc=BPath()
			find_directory(directory_which.B_SYSTEM_DOCUMENTATION_DIRECTORY,perc,False,None)
			link=perc.Path()+"/HaiQR2/index.html"
			ent=BEntry(link)
			if ent.Exists():
				# open system documentation help
				cmd = "open "+link
				t = Thread(target=os.system,args=(cmd,))
				t.run()
			else:
				find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
				link=perc.Path()+"/HaiQR2/Data/help/index.html"
				ent=BEntry(link)
				if ent.Exists():
					#open user installed help
					cmd = "open "+link
					t = Thread(target=os.system,args=(cmd,))
					t.run()
				else:
					cwd = os.getcwd()
					link=cwd+"/Data/help/index.html"
					ent=BEntry(link)
					if ent.Exists():
						#open git downloaded help
						cmd = "open "+link
						t = Thread(target=os.system,args=(cmd,))
						t.run()
					else:
						wa=BAlert('noo', 'No help pages installed', 'Poor me', None,None,InterfaceDefs.B_WIDTH_AS_USUAL,alert_type.B_WARNING_ALERT)
						wa.Go()
			return

		BWindow.MessageReceived(self, msg)
		
	def FrameResized(self,x,y):
		self.bckgnd.ResizeTo(x,y)#self.bckgnd.Bounds().left,self.bckgnd.Bounds().top,self.bckgnd.Bounds().right+x,self.bckgnd.Bounds().bottom+y)
		self.bar.ResizeTo(self.bckgnd.Bounds().right,self.bar.Bounds().bottom)
		self.underlist.ResizeTo(self.bckgnd.Bounds().right,self.bckgnd.Bounds().bottom-self.bar.Bounds().Height())
		self.qrframe.ResizeTo(x-60,y-self.bar.Bounds().Height()-60-self.tachetest.Bounds().Height()-24)
		self.qrframe.Refresh()
	def QuitRequested(self):
		#del self.ofp
		#del self.fp
		print ("So long and thanks for all the fish")
		return BWindow.QuitRequested(self)

class App(BApplication):
    def __init__(self):
        BApplication.__init__(self, "application/x-HaiQR-python3")
        self.txtpath=""
    def ReadyToRun(self):
        self.window = HaiQRWindow(BRect(100,80,600,600))
        self.window.Show()
    def RefsReceived(self, msg):
        #msg.PrintToStream()
        if msg.what == B_REFS_RECEIVED:
            i = 0
            while 1:
                try:
                #if True:
                    e=entry_ref()
                    rino = msg.FindRef("refs", i,e)
                    entryref = BEntry(e,True)
                    bpatho=BPath()
                    entryref.GetPath(bpatho)
                    self.txtpath= bpatho.Path()
                    ###### CHECK FOR IMAGE MIME TYPE
                    mime = BMimeType()
                    BMimeType.GuessMimeType(self.txtpath,mime)
                    mimetype = repr(mime.Type())
                    supertype,subtype = mimetype.split('/')
                    if (supertype.replace('\'','') == "image"):
                        if mime.IsInstalled():
                            pass #I can use the image
                        else:
                            #I cannot use this image
                            z = BAlert('Nimg', 'I cannot use this image\nSelect another one?', 'Yes', 'No', None, InterfaceDefs.B_WIDTH_AS_USUAL,alert_type.B_WARNING_ALERT)
                            ret = z.Go()
                            if ret == 1:
                                break # aborts adding logo
                            else:
                                # Retry: open panel
                                be_app.WindowAt(0).PostMessage(6)
                                be_app.WindowAt(0).PostMessage(5)
                                break
                    else:
                        #"It's not an image"
                        be_app.WindowAt(0).PostMessage(5)
                        z = BAlert('Nimg', 'This is not an image\nRetry?', 'Yes', 'No', None, InterfaceDefs.B_WIDTH_AS_USUAL,alert_type.B_WARNING_ALERT)
                        ret = z.Go()
                        if ret == 1:
                            break # aborts adding logo
                        else:
                            # Retry: open panel
                            be_app.WindowAt(0).PostMessage(6)
                            be_app.WindowAt(0).PostMessage(5)
                            break
                    a=BMessage(112)
                    a.AddString("path=",self.txtpath)
                    be_app.WindowAt(0).PostMessage(a)
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
            be_app.WindowAt(0).PostMessage(messaggio)
            return
        elif msg.what == B_CANCEL:
            if self.txtpath=="":
                #se nissun file di salvaa
                be_app.WindowAt(0).PostMessage(BMessage(5))
                be_app.WindowAt(0).PostMessage(BMessage(6))
            else:
                #se file viert inzorne imagjin
                be_app.WindowAt(0).PostMessage(BMessage(4))
                be_app.WindowAt(0).PostMessage(BMessage(6))
            return
			
        elif msg.what == 11:
            #Fix for bug: "Default button" is disabled on fp.Show()
            be_app.WindowAt(1).PostMessage(B_KEY_DOWN)
            return
			
        elif msg.what == 311:
            self.txtpath = ""
            return

def main():
    global be_app
    be_app = App()
    be_app.Run()
 
if __name__ == "__main__":
    main()
