#!/boot/system/bin/python3
jes=False
try:
	from Be import BApplication, BWindow, BBox, BRect, BTextControl, BView, BMenu, BMenuBar, BMenuField, BMenuItem, BSeparatorItem, AppDefs, BFont, BDirectory, BFile
	from Be import BMessage, BBitmap, BTextView, BButton, BStringItem, window_type, B_NOT_RESIZABLE, B_QUIT_ON_WINDOW_CLOSE, B_CLOSE_ON_ESCAPE
	from Be import BStringView, BMimeType, BPoint, BAlert,BPath,InterfaceDefs,BScreen
	from Be.View import *
	from Be.FindDirectory import *
	from Be.GraphicsDefs import *
	from Be.Alert import alert_type
	from Be.AppDefs import *
	from Be.View import *#B_WILL_DRAW,B_FOLLOW_NONE,B_FOLLOW_ALL_SIDES,B_FOLLOW_ALL,B_NAVIGABLE,B_FOLLOW_LEFT,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT_RIGHT,B_FOLLOW_RIGHT,B_FULL_UPDATE_ON_RESIZE
	from Be.TextView import text_run
	from Be.FilePanel import *
	from Be.Font import be_plain_font, be_bold_font
	from Be.InterfaceDefs import border_style
	from Be.TypeConstants import *
	from Be import BEntry,BUrl,BTranslationUtils
	from Be.Entry import entry_ref
	from Be.Entry import get_ref_for_path
	from Be.Errors import B_OK
	from Be.Accelerant import display_mode
	from Be.StorageDefs import B_READ_WRITE,B_WRITE_ONLY,B_READ_ONLY
except:
	print("error loading Haiku-PyAPI modules")
	jes = True

import tempfile, os, sys, struct, locale, gettext
from threading import Thread
from random import randrange
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



def Ent_config():
	perc=BPath()
	find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
	#datapath=BDirectory(perc.Path()+"/HaiQR2")
	#ent=BEntry(datapath,perc.Path()+"/HaiQR2")
	ent=BEntry(perc.Path()+"/HaiQR2")
	if not ent.Exists() and ent.IsDirectory():
		#datapath.CreateDirectory(perc.Path()+"/HaiQR2", None)#datapath)
		BDirectory().CreateDirectory(perc.Path()+"/HaiQR2", None)
	ent.GetPath(perc)
	confile=BPath(perc.Path()+'/settings.cfg',None,False)
	ent=BEntry(confile.Path())
	return(ent,confile.Path())

def openlink(link):
	osd=BUrl(link)
	retu=osd.OpenWithPreferredApplication()

def lookfdata(name):
	perc=BPath()
	find_directory(directory_which.B_SYSTEM_DATA_DIRECTORY,perc,False,None)
	ent=BEntry(perc.Path()+"/HaiQR2/"+name)
	if ent.Exists():
		#use mascot installed in system data folder
		ent.GetPath(perc)
		return (True,perc.Path())
	else:
		find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
		ent=BEntry(perc.Path()+"/HaiQR2/"+name)
		if ent.Exists():
			#use mascot installed in user data folder
			ent.GetPath(perc)
			return (True,perc.Path())
		else:
			nopages=True
			cwd = os.getcwd()
			ent=BEntry(cwd+"/data/"+name)
			if ent.Exists():
				#use mascot downloaded with git by cmdline
				ent.GetPath(perc)
				return (True,perc.Path())
				nopages=False
			else:
				alt="".join(sys.argv)
				mydir=os.path.dirname(alt)
				link=mydir+"/data/"+name
				ent=BEntry(link)
				if ent.Exists():
					ent.GetPath(perc)
					return (True,perc.Path())
					nopages=False
			if nopages:
				return (False,None)
class LocalizItem(BMenuItem):
	def __init__(self,name):
		self.name=name
		msg=BMessage(600)
		msg.AddString("name",self.name)
		BMenuItem.__init__(self,self.name,msg,'\x00',0)

locale_dir=None
b,p=lookfdata("locale")
lt=[]
if b:
	if BEntry(p).IsDirectory():
		locale_dir=p
		#creare lista di traduzioni disponibili
		dir=BDirectory(p)
		ent=BEntry()
		dir.Rewind()
		ret = False
		while not ret:
			ret=dir.GetNextEntry(ent,True)
			if not ret:
				perc=BPath()
				ent.GetPath(perc)
				lt.append(perc.Leaf())

########### TODO INTEGRARE PERCORSI DI INSTALLAZIONE
b,p=lookfdata("index.html")
if b:
	if jes:
		j = Thread(target=openlink,args=(p,))
		j.run()
############################################################################

def save_config(config_data):
	if isinstance(config_data,list):
		message = BMessage(0)
		try:
			ordered_config_data = sorted(config_data, key=lambda config: config['indice'])
			for config in ordered_config_data:
				if config['tipo'] == B_STRING_TYPE:
					message.AddString(config['nome'], config['valore'])
				elif config['tipo'] == B_INT32_TYPE:
					message.AddInt32(config['nome'], config['valore'])
				elif config['tipo'] == B_BOOL_TYPE:
					message.AddBool(config['nome'], config['valore'])
				#jj,ll=lookfdata(".")
				ent,path=Ent_config()
				if ent.Exists():
					file=BFile(path,B_READ_WRITE)
				else:
					dir=BDirectory()
					ent.GetParent(dir)
					file=BFile()
					ret=dir.CreateFile(path,file)
				#dir=BDirectory(ll)
				#file=BFile()
				#ret=dir.CreateFile(ll+"/settings.cfg",file)
				message.Flatten(file)
				file.Unset()
				#del file
				return True
		except Exception as e:
			print(f"Errore durante l'aggiunta o la scrittura dei dati: {e}")
			return False
	elif isinstance(config_data,BMessage):
		ent,path=Ent_config()
		file = BFile(path, B_WRITE_ONLY)
		config_data.Flatten(file)

def load_config(path):
	message = BMessage()
	configuration_data = []
	try:
		message.Unflatten(BFile(path,0))
		ntot=message.CountNames(B_ANY_TYPE)
		i=0
		while i<ntot:
			typ=B_ANY_TYPE
			ret=message.GetInfo(typ,i)
			if ret[0]==B_OK:
				if ret[2] == B_STRING_TYPE:
					c=0
					while c<ret[3]:
						status,valore=message.FindString(ret[1],c)
						diz={'indice': i, 'nome': ret[1], 'tipo': ret[2], 'conteggio': c, 'valore':valore}
						c+=1
				elif ret[2] == B_INT32_TYPE:
					c=0
					while c<ret[3]:
						status,valore=message.FindInt32(ret[1],c)
						diz={'indice': i, 'nome': ret[1], 'tipo': ret[2], 'conteggio': c, 'valore':valore}
						c+=1
				elif ret[2] == B_BOOL_TYPE:
					c=0
					while c<ret[3]:
						status,valore=message.FindInt32(ret[1],c)
						diz={'indice': i, 'nome': ret[1], 'tipo': ret[2], 'conteggio': c, 'valore':valore}
						c+=1
				configuration_data.append(diz)
			i+=1
		return configuration_data
	except Exception as e:
		print(f"Errore durante il caricamento del file di configurazione: {e}")
		return None

jk,kl=lookfdata("settings.cfg")
if not jk:
	save_config([{'indice': 0, 'nome': "localization", 'tipo': B_STRING_TYPE, 'conteggio': 1, 'valore':locale.getlocale()[0]}])

ent,path=Ent_config()
if ent.Exists():
	cd=load_config(path)
	if cd != None:
		found=False
		for itm in cd:
			if itm["nome"]=="localization":
				loc=[itm["valore"]]
				found=True
				break
		if not found:
			loc=locale.getlocale()
	else:
		loc=locale.getlocale()
else:
	loc=locale.getlocale()

if locale_dir!=None:
	if loc[0] in lt:
		try:
			t = gettext.translation(
				domain="haiqr",  # nome del progetto
				localedir=locale_dir,
				languages=[loc[0]],
				fallback=True  # se la lingua non esiste usa inglese
			)
		except Exception as e:
			print(f"Error loading translations: {e}")
			t = gettext.NullTranslations()
	else:
		t = gettext.NullTranslations()
else:
	t = gettext.NullTranslations()
			
global _
_ = t.gettext

def byte_count(stringa, encoding='utf-8'):
		byte_counts = []
		start = 0
		total = 0
		for char in stringa:
			end = start + len(char.encode(encoding))
			total+=(end- start)
			byte_counts.append((char,end - start))
			start = end
		return (total,byte_counts)

def find_byte(lookf,looka,offset=0):
	#note offset is not byte-offset but char-offset
	retc=looka.find(lookf,offset)
	if retc>-1:
		trunc=looka[:retc]
		return byte_count(trunc)[0]
	else:
		return -1
# Translators: The app name, don't translate, only transliterate
appname=_("HaiQR2")
version="2.1"
# Translators: state of release like: alpha, beta, release
state=_("alpha")

class PView(BView):
	def __init__(self,frame,name,immagine):
		self.immagine=immagine
		self.frame=frame
		BView.__init__(self,frame,name,8, 20000000)#4660, 2000000|8000000)
		self.SetFlags(B_WILL_DRAW)
		self.SetResizingMode(B_FOLLOW_ALL_SIDES)
		
		self.dragmsg=struct.unpack('!l', b'MIME')[0]
		
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
	def MessageReceived(self, msg):
		#msg.PrintToStream()
		if msg.what == self.dragmsg:
			ntot=msg.CountNames(B_MIME_TYPE)
			i=0
			while i<ntot-1:
				l=[]
				rtyp=0
				cont=0
				ret=msg.GetInfo(B_MIME_TYPE,i,l,rtyp,cont)
				print("vecchio metodo",l,rtyp,cont)
				ret=msg.GetInfo(B_MIME_TYPE,i) # NEW VERSION OF HAIKU-PYAPI
				#print(ret[1],ret[2],ret[3])
				xmsg=BMessage(73570)
				xmsg.AddString("text",msg.FindData(ret[1],ret[2])[1].decode('utf-8'))
				be_app.WindowAt(0).PostMessage(xmsg)
				i+=1
			return
		BView.MessageReceived(self,msg)



class CustomLang(BWindow):
	myItems=[]
	alerts=[]
	def __init__(self):
		a=display_mode()
		BScreen().GetMode(a)
		w=a.virtual_width
		h=a.virtual_height
		fon=BFont()
		# Translators: window title
		BWindow.__init__(self, BRect(w/2-200, h/2-fon.Size()-10, w/2+200, h/2+(fon.Size()*2.5)),"CustomLang",window_type.B_BORDERED_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		self.bckgnd=BBox(self.Bounds(),"bckgnd_customlang",B_FOLLOW_NONE,B_WILL_DRAW,border_style.B_NO_BORDER)
		
		self.AddChild(self.bckgnd,None)
		self.menulocaliz=BMenu(_("Localizations"))
		self.menulocaliz.SetLabelFromMarked(True)
		bounds=self.bckgnd.Bounds()
		l=bounds.left
		t=bounds.top
		r=bounds.right
		b=bounds.bottom
		self.bottomstring=BStringView(BRect(l,b-fon.Size(),r,b),"hint",_("Note: any change requires a restart"))
		for y in lt:
			self.myItems.append(LocalizItem(y))#<fix doublefree
			self.menulocaliz.AddItem(self.myItems[-1])
		self.menuloc = BMenuField(BRect(5,5,r-5,b-5), 'pop0', _("Interface localization"), self.menulocaliz,B_FOLLOW_TOP)
		self.bckgnd.AddChild(self.menuloc,None)
		self.bckgnd.AddChild(self.bottomstring,None)
		
	def MessageReceived(self, msg):
		if msg.what == 600:
			be_app.WindowAt(0).PostMessage(msg)
			self.Quit()
			return
		return BWindow.MessageReceived(self,msg)



class AboutWindow(BWindow):
	def __init__(self):
		scr=BScreen()
		scrfrm=scr.Frame()
		x=(scrfrm.right+1)/2-550/2
		y=(scrfrm.bottom+1)/2-625/2
		BWindow.__init__(self, BRect(x, y, x+550, y+625),_("About"),window_type.B_MODAL_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		self.bckgnd = BView(self.Bounds(), "backgroundView", 8, 20000000)
		self.bckgnd.SetResizingMode(B_FOLLOW_V_CENTER|B_FOLLOW_H_CENTER)
		bckgnd_bounds=self.bckgnd.Bounds()
		self.AddChild(self.bckgnd,None)
		self.box = BBox(bckgnd_bounds,"Underbox",0x0202|0x0404,border_style.B_FANCY_BORDER)
		self.bckgnd.AddChild(self.box,None)
		################## PBOX ###############################
		sta=(self.box.Bounds().Width()/2)-119
		end=(self.box.Bounds().Width()/2)+119
		pbox_rect=BRect(sta,5,end,238)
		b,p=lookfdata("HaiQR.png")
		if b:
			img1=BTranslationUtils.GetBitmap(p,None)
			self.pbox=PView(pbox_rect,"PictureBox",img1)
			self.box.AddChild(self.pbox,None)
		else:
			print("manca l'immagine")
			rec=self.box.Bounds()
			fontina=BFont()
			self.box.GetFont(fontina)
			hf=fontina.Size()
			mistxt=_("image missing")
			sw=fontina.StringWidth(mistxt)
			recsv=BRect(rec.Width()/2-sw/2,rec.Height()/2-hf/2-242-2,rec.Width()/2+sw/2,rec.Height()/2+hf/2-242+2)
			self.pbox=BStringView(recsv,"picture_missing",mistxt)
			self.box.AddChild(self.pbox,None)
		abrect=BRect(2,242, self.box.Bounds().Width()-2,self.box.Bounds().Height()-2)
		inner_ab=BRect(4,4,abrect.Width()-4,abrect.Height()-4)

		self.AboutText = BTextView(abrect, 'aBOUTTxTView', inner_ab , B_FOLLOW_NONE)
		self.AboutText.MakeEditable(False)
		self.AboutText.MakeSelectable(False)
		self.AboutText.SetStylable(True)
		ts1=_("version")#\t-\t
		ts2=_("\n\nA simple QR generator for Haiku.\n\nThis is a simple QR generator written in Python 3.10 + Haiku-PyAPI and qrcode module\n\n")
		ts3=_(" is a reworked update of HaiQR which used python2 and Bethon.\n\nThis version is in ")
		ts4=_(" state\n\t\t\t\t\t\t\t\t\tdesigned by Fabio Tomat (TmTFx)\n\n\t\tpress ESC to close this window")
		stuff=" ".join((appname,ts1,version,ts2,appname,ts3,state,ts4))
		arra=[]
		i = len(appname)
		c=0
		fon1=BFont(be_bold_font)
		fon1.SetSize(48.0)
		while c<i:
			arra.append(text_run())
			arra[-1].offset=c
			arra[-1].font=fon1
			col=rgb_color()
			col.red=0
			col.green=0
			col.blue=randrange(50,200)
			col.alpha=200
			arra[-1].color=col
			c+=1
		n=find_byte("version",stuff)
		txtrun2=text_run()
		txtrun2.offset=n
		txtrun2.font=be_plain_font
		col2=rgb_color()
		col2.red=0
		col2.green=0
		col2.blue=0
		col2.alpha=0
		txtrun2.color=col2
		arra.append(txtrun2)
		self.AboutText.SetText(stuff,arra)
		self.box.AddChild(self.AboutText,None)

	def WindowActivated(self, active):
		if active:
			self.AboutText.Invalidate()
			self.box.Invalidate()
			self.pbox.Invalidate()
		BWindow.WindowActivated(self, active)

	def QuitRequested(self):
		be_app.WindowAt(0).Activate() #sometimes it doesn't happen (why?) so we try to force it
		return BWindow.QuitRequested(self)


class HaiQRWindow(BWindow):
	addlogo=_("Add Logo")
	Menus = (
		(_('File'), ((1, _('Generate QR')),(2, _('Save QR')),(5, addlogo),(None, None),(7, _("Set Language")),(None, None),(AppDefs.B_QUIT_REQUESTED, _('Quit')))),
		(_('Help'), ((8, _('Help')),(3, _('About'))))
		)
	alerts=[]
	def __init__(self, frame,arg):
		selectionmenu=0
		BWindow.__init__(self, frame, _('QR generator for Haiku'), window_type.B_TITLED_WINDOW,B_QUIT_ON_WINDOW_CLOSE)#|B_CLOSE_ON_ESCAPE)
		bounds = self.Bounds()
		self.bckgnd = BView(bounds, "background",8, 20000000)
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
		labello=_("Paste here:")
		wid=a.StringWidth(labello)
		whereplace=BRect(30,underbounds.Height()-barheight-30,30+wid,underbounds.Height()-barheight-10)
		self.Hintlabel= BStringView(whereplace,"Label",labello)
		##### this is a workaround####
		self.underlist.AddChild(self.Hintlabel,None)
		self.Hintlabel.Hide()
		######## end of workaround ##########################
		self.tachetest=BTextControl(BRect(7,underbounds.Height()-barheight-27,underbounds.Width()-57,underbounds.Height()-barheight-17),'TxTView', labello,None,BMessage(1),B_FOLLOW_LEFT_RIGHT | B_FOLLOW_BOTTOM)
		self.tachetest.SetDivider(wid+5)
		self.underlist.AddChild(self.tachetest,None)
		self.tachetest.MakeFocus(1)
		#self.BUTTON_MSG = struct.unpack('!l', 'PRES')[0]
		self.QRButton = BButton(BRect(underbounds.Width()-53, underbounds.Height()-barheight-32, underbounds.Width()-5, underbounds.Height()-barheight-10), "QRit", _("QR it!"), BMessage(1), B_FOLLOW_RIGHT | B_FOLLOW_BOTTOM)
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
		if arg!="":
			self.tachetest.SetText(arg)
			be_app.WindowAt(0).PostMessage(1)
			
		

	def MessageReceived(self, msg):
		if msg.what == 1:
			#Gjenere QR
			if self.tachetest.Text() != "":
				self.imginmemory = True
				self.qr.clear()
				self.qr.add_data(self.tachetest.Text())
				self.qr.make(fit=True)
				self.qrimg=self.qr.make_image(fill_color="black",back_color="white")#.convert('RGB')
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
			
		elif msg.what == 2:
			#SaveFilePanel
			if self.qrcreated:
				self.CanOpenPanel=False
				self.fp.Show()
				#be_app.PostMessage(BMessage(11))
			return

		elif msg.what == 54173:
			#Save qr
			b=entry_ref()
			self.fp.GetPanelDirectory(b)
			c=BEntry(b)
			d=BPath()
			c.GetPath(d)
			savepath=d.Path()
			status,e = msg.FindString("name")
			completepath = savepath +"/"+ e
			self.qrimg.save(completepath)
			return

		elif msg.what == 3:
			#ABOUT
			self.About = AboutWindow()
			self.About.Show()
			return
			
		elif msg.what == 4:
			if self.qrcreated:
				be_app.WindowAt(0).PostMessage(BMessage(1))
			return
				
		elif msg.what == 5:
			if not(self.ofp.IsShowing()):
			#ADD OR REMOVE LOGO
				if self.bar.FindItem(self.addlogo).IsMarked():
					#remove logo
					self.logopath=""
					self.bar.FindItem(self.addlogo).SetMarked(0)
					be_app.PostMessage(BMessage(311))
					if self.qrcreated:
						be_app.WindowAt(0).PostMessage(BMessage(1))
				else:
					if self.CanOpenPanel:
						#add logo
						self.bar.FindItem(self.addlogo).SetMarked(1)
						self.ofp.Show()
						self.CanOpenPanel=False
			return

		elif msg.what == 6:
			self.CanOpenPanel=True
			return
		
		elif msg.what == 7:
			self.CustLang=CustomLang()
			self.CustLang.Show()
			
		elif msg.what == 112:
			status,self.logopath = msg.FindString("path=")
			return
			
		elif msg.what == 8:
			#HELP
			perc=BPath()
			find_directory(directory_which.B_SYSTEM_DOCUMENTATION_DIRECTORY,perc,False,None)
			link=perc.Path()+"/packages/haiqr/HaiQR2/index.html"
			ent=BEntry(link)
			if ent.Exists():
				# open system documentation help
				cmd = "open "+link
				t = Thread(target=os.system,args=(cmd,))
				t.run()
			else:
				find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
				link=perc.Path()+"/HaiQR2/data/index.html"
				ent=BEntry(link)
				if ent.Exists():
					#open user installed help
					cmd = "open "+link
					t = Thread(target=os.system,args=(cmd,))
					t.run()
				else:
					nopages=True
					cwd = os.getcwd()
					link=cwd+"/data/index.html"
					ent=BEntry(link)
					if ent.Exists():
						#open git downloaded help by cmdline
						cmd = "open "+link
						t = Thread(target=os.system,args=(cmd,))
						t.run()
						nopages=False
					else:
						alt="".join(sys.argv)
						mydir=os.path.dirname(alt)
						link=mydir+"/data/index.html"
						ent=BEntry(link)
						if ent.Exists():
							#open git downloaded help bygraphiclaunch
							cmd = "open "+link
							t = Thread(target=os.system,args=(cmd,))
							t.run()
							nopages=False
					if nopages:
						wa=BAlert('noo', _('No help pages installed'), _('Poor me'), None,None,InterfaceDefs.B_WIDTH_AS_USUAL,alert_type.B_WARNING_ALERT)
						self.alerts.append(wa)
						wa.Go()
			return
		elif msg.what==73570:
			status,txxt=msg.FindString("text")
			if status==B_OK:
				self.tachetest.SetText(txxt)
		elif msg.what==600:
			status,lang=msg.FindString("name")
			if status==B_OK:
				ent,path=Ent_config()
				if ent.Exists():
					cd=load_config(path)
					for i in cd:
						if i['nome'] == "localization":
							i["valore"]=lang
							save_config(cd)
							break
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
		#be_app.Quit()
		return BWindow.QuitRequested(self)

class App(BApplication):
	realargs=""
	def __init__(self):
		BApplication.__init__(self, "application/x-HaiQR-python3")
		self.txtpath=""
		self.alerts=[]
	def ReadyToRun(self):
		rect=BRect(100,80,600,600)
		if len(self.realargs) == 0:
			self.window = HaiQRWindow(rect,"")
		else:
			self.window = HaiQRWindow(rect,self.realargs)
		
		self.window.Show()
	def RefsReceived(self, msg):
		#msg.PrintToStream()
		if msg.what == B_REFS_RECEIVED:
			i = 0
			while 1:
				try:
					#old way
					#e=entry_ref()
					#rino = msg.FindRef("refs", i,e)
					status,e=msg.FindRef("refs",i)
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
							z = BAlert('Nimg', _('I cannot use this image\nSelect another one?'), _('Yes'), _('No'), None, InterfaceDefs.B_WIDTH_AS_USUAL,alert_type.B_WARNING_ALERT)
							self.alerts.append(z)
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
						z = BAlert('Nimg', _('This is not an image\nRetry?'), _('Yes'), _('No'), None, InterfaceDefs.B_WIDTH_AS_USUAL,alert_type.B_WARNING_ALERT)
						self.alerts.append(z)
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
	def ArgvReceived(self,num,args):
		if args[1][-8:]=="HaiQR.py" or args[1][-5:]=="HaiQR":
			#launched by terminal or by link in non-packaged/bin
			args.pop(1)
			args.pop(0)
			joinedrealargs=" ".join(args)
			self.realargs=joinedrealargs
	def MessageReceived(self, msg):
		if msg.what == B_SAVE_REQUESTED:
			status,e = msg.FindString("name")
			if status == B_OK:
				messaggio = BMessage(54173)
				messaggio.AddString("name",e)
				be_app.WindowAt(0).PostMessage(messaggio)
			return
		elif msg.what == B_CANCEL:
			if self.txtpath=="":
				#se nissun file di salvâ
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
