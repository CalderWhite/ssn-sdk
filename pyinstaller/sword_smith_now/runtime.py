import pygame, time, random, sys, chunkObject, json, guiObjects, os
import PIL.Image, PIL.ImageFilter
from GMK.items import mineral_constructor
class font_collection(object):
	def __init__(self):
		"""This is really just an empty skeleton so I can organize my code."""
		self.title_mc = pygame.font.Font("fonts/Minecrafter_3.ttf",24)
		self.pause_f = pygame.font.Font("fonts/PressStart2P.ttf",24)
		self.courb = pygame.font.Font("fonts/courbd.ttf",16)
	def add(self,name,filename,size):
		"""Honestly, I don't even know if this method is neccesary."""
		self.__setattr__(name,pygame.font.Font(filename,size))
class audio_manager(object):
	def log(self,msg,level="INFO",user="AUDIO"):
		self.parent.log(msg,level=level,user=user)
	def __init__(self,parent):
		self.muted = False
		pass
	def mute(self):
		pygame.mixer.music.stop()
		self.muted = True
	def unmute(self):
		self.muted = False
		# don't play the music, since there might not have been any playing
	def play_and_load_music(self,filename,loops=0):
		if self.muted == False:
			pygame.mixer.music.load(filename)
			pygame.mixer.music.play(loops)
	def load_audio(self):
		#pygame.mixer.music.load("audio/music/tracks/theme_baseline.mp3")
		# nothing to load right now
		pass
class new_player(object):
	def __init__(self,name,parent):
		self.name = name
		self.x = 0#parent.current_chunk.get_rect()[0] / 2
		self.y = 0#parent.current_chunk.get_rect()[1] / 2
		self.speed = 1
		self.hitbox = (60,120)
		self.rect = (60,120)
		self.parent = parent
		self.possesions = self.possesion_class()
	def check_movement(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
			self.speed = 10
		elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
			self.speed = 0.5
		else:
			self.speed = 1
		# create offset variables so we aren't changing the player's x and y right away
		xoff = 0
		yoff = 0
		# set offset variables
		if keys[pygame.K_w]:
			# positive effect
			yoff+=1 * self.speed
			pass
		if keys[pygame.K_s]:
			# negative effect
			yoff-=1 * self.speed
			pass
		if keys[pygame.K_d]:
			# positive effect
			xoff+=1 * self.speed
			pass
		if keys[pygame.K_a]:
			# negative effect
			xoff-=1 * self.speed
			pass
		check = self.check_collision(xoff,yoff)
		#print(check)
		if check == True:
			self.x+= xoff
			self.y+= yoff
		else:
			self.x,self.y = check
	def check_collision(self,xoff,yoff):
		# first check outline
		useless1,useless2,w,h=self.parent.current_chunk.get_rect()
		#print(w,h)
		# at some point I may want to change this, so I'll just use these variables from the start.
		minx = (w/2) * -1
		miny = h/2 * -1
		maxx = w/2
		maxy = h/2
		newx = self.x + xoff
		newy = self.y + yoff
		rx = None
		ret = False
		#print(newx,newy)
		if newy > maxy:
			newy = maxy
			ret = True
		elif newy < miny:
			newy = miny
			ret = True
		if newx > maxx:
			newx = maxx
			ret = True
		elif newx < minx:
			newx = minx
			ret = True
		if ret:
			return (newx,newy)
		# --------------------------------------------------------------------
		# now check all the game/gui's objects
		for obj in self.parent.gui.chunk_objects:
			# write a bunch of variables to simplify
			# add half the player's height / width for checks, so that the player can't go half through a block
			# easier access to the rect
			width, height = self.rect
			# Left x inbetweent, initial x inbetween
			Lxi = newx - width >= obj.x and newx - width <= obj.x + obj.width
			Lixi = self.x - width/2>= obj.x and self.x - width/2 <= obj.x + obj.width
			# Right x inbetweent, initial x inbetween
			Rxi = newx + width/2 >= obj.x and newx + width/2 <= obj.x + obj.width
			Rixi = self.x + width/2 >= obj.x and self.x + width/2 <= obj.x + obj.width
			# Middle (object is smaller than player)
			Mixg =  self.x + width/2 > obj.x + obj.width and self.x - width/2 <= obj.x - obj.width
			# ---------------------------------------------------------------------------------------
			# y stuff
			# checking the bottom edge of the player (If hitting the top edge of the object)
			Tyi = newy - height/2 <= obj.y and newy - height/2 >= obj.y - obj.height
			Tiyi = self.y - height/2 <= obj.y and self.y - height/2 >= obj.y - obj.height
			# checking the Top edge of the player (If hitting the bottom edge of the object)
			Byi = newy + height/2 >= obj.y - obj.height and newy + height/2 <= obj.y# + obj.height
			Biyi = self.y + height/2 >= obj.y - obj.height and self.y + height/2 <= obj.y#a + obj.height
			# checking the middle (If both the top and bottom edge of the player are outside the object)
			Myi = self.y + height/2 >= obj.y and self.y - height/2 <= obj.y - obj.height
			Miyi = newy + height/2 >= obj.y and newy - height/2 <= obj.y - obj.height
			# initial y is less than that the
			ily = self.y <= obj.y
			# newy is greater than the object's y
			ngy = newy >= obj.y
			# moving upwards
			mup = newy + height/2 >= obj.y - obj.height and self.y + height/2 <= obj.y - obj.height
			# moving downwards
			mdwn = newy - height/2 <= obj.y and self.y - height/2 >= obj.y
			# moving left/right
			mlft = newx - width/2 <= obj.x + obj.width and self.x - width/2 >= obj.x + obj.width
			mrgt = newx + width/2 >= obj.x and self.x + width/2 <= obj.x
			#print(newx - width/2,obj.x + obj.width)
			#print(self.y,obj.y,obj.y - obj.height)
			#print(Tyi and Tiyi,Byi and Biyi, Myi and Miyi)
			#-------------------------------------
			# first as if we are moving along the y axis
			if Lixi and Lxi or Rixi and Rxi:
				##print(self.y,obj.y + obj.height,newy)
				if mup:
					# basically hit the object
					newy = obj.y - obj.height - height/2
					#print("Moving up...")
				elif mdwn:
					newy = obj.y + height/2
					#print("Moving down...")
			# now as if we were moving along the x axis
			if Tiyi or Biyi or Miyi:
				if mrgt:
					newx = obj.x - width/2
				elif mlft:
					newx = obj.x + obj.width + width/2
			# collisions for below the object (diagonal motion)
			if ily and ngy:
				if self.x <= obj.x and newx >= obj.x or self.x >= obj.x + obj.width and newx <= obj.x + obj.width:
					newy = obj.y
					newx = obj.x
					#print("Moving diagonally upwards...")
					break
			pass
		return (newx,newy)
	class possesion_class(object):
		"""This is just to organize. Use this class through the main class, instead of creating an instance."""
		def __init__(self):
			self.minerals = {}
		def give(self,item_type,obj,quantity):
			"""Types (as of now):
			0 : mineral
			"""
			if item_type == 0:
				if self.minerals.__contains__(obj.name):
					self.minerals[obj.name].add(quantity)
				else:
					self.minerals[obj.name] = item_manager.mineral_counter(obj)
					self.minerals[obj.name].add(quantity)
		def take(self,item_type,obj,quantity):
			if item_type == 0:
				if self.minerals.__contains__(obj.name):
					self.minerals[obj.name].remove(quantity)
				else:
					print("ERROR: ITEM WAS ATTEMPTED TO BETAKEN FROM USER BUT USER HAS NONE OF THAT ITEM")
	def give_all(self,quantity=999):
		for m in self.parent.item_manager.minerals:
			self.possesions.give(0,self.parent.item_manager.minerals[m],quantity)
class gui(object):
	def __init__(self,parent):
		"""Defines the function and boots at the same time. (Logs stuff and loads stuff)"""
		self.parent = parent
		parent.log("Initializing pygame...",user="GUI")
		pygame.init()
		# whatever you do, you MUST make the height and width of the display divisable by two
		self.screen = pygame.display.set_mode( (600,600))
		pygame.display.set_caption(parent.parent.game_name)
		parent.log("Loading images....",user="GUI")
		self.icon = pygame.image.load("images/icon.png")
		self.icon = pygame.transform.scale(self.icon, (32,32) )
		parent.log("Setting window icon...",user="GUI")
		pygame.display.set_icon(self.icon)
		parent.log("Loading and setting cursor...",user="GUI")
		self.load_cursors()
		self.set_cursor("regular")
		pygame.mouse.set_visible(False);
		parent.log("Loading chunks...",user="GUI")
		self.load_chunks()
		parent.log("Loading objects [trees,bushes, etc.]...")
		self.chunk_objects = [chunkObject.rect([-100,-100,100,100],(123,43,200)),chunkObject.rect([-100,200,100,100],(0,0,0))]
		self.custom_events = {}
		pass
	def check_events(self,key_bindings=True):
		eventz = pygame.event.get()
		for event in eventz:
			if event.type == pygame.QUIT:
				self.parent.quit()
				break
			elif event.type == pygame.KEYDOWN:
				if key_bindings:
					self.parent.key_bindings.check_all(event)
			for ce in self.custom_events:
				if event.type == ce:
					self.custom_events[ce](event)
	def load_cursors(self):
		self.cursors = {}
		d = os.listdir("images/cursors")
		for c in d:
			if c != "Thumbs.db":
				self.cursors[c.split(".")[0]] = pygame.image.load("images/cursors/" + c).convert_alpha()
	def set_cursor(self,name):
		self.cursor = self.cursors[name]
	def add_event(self,t):
		self.custom_events[t[0]] = t[1]
	def load_chunks(self):
		"""Experimental so far. Only works in dev mode"""
		if self.parent.mode == 1:
			# only for dev mode
			self.chunks = []
			self.chunks.append(pygame.image.load("./saves/chunk_2.png"))
	def render_floor(self):
		"""renders floor (background)."""
		sheight,swidth = pygame.display.get_surface().get_size()
		crop = pygame.Surface(pygame.display.get_surface().get_size())
		# invert the y in offsets so we get a four quadrent coordinet system
		# we also add half the sheight and swidth of the chunk to create the four quadrent system
		# ---------------------------------------------------------------------------------------------
		# subtract swidth and sheight (divided by two) to accomodate for the display
		# Explanation:
		# if the offset was 0,0 (player's x and y would be (-7200,7200)) then
		# it would display the top left corner, but It wouldn't go off screen, meaning the PLAYER isn't acutally
		# at 0,0 ; they're at (swidth/,sheight/2)
		# Consequently if the player was at the very bottom of the chunk, there would be nothing since they are off the chunk.
		# DERP idk ^^^
		xo = (int(self.chunks[0].get_size()[0] / 2) + self.parent.player.x) - swidth / 2
		yo = (int(self.chunks[0].get_size()[1] / 2 + (self.parent.player.y * -1))) - sheight / 2
		crop.blit(self.parent.current_chunk,(0,0),(xo,yo,swidth,sheight))
		#print(self.parent.player.x,self.parent.player.y)
		self.screen.blit(crop,(0,0))
	def render_objects(self):
		"""Renders all the objects from self.chunk_objects. Which should contain chunkObject objects."""
		# honestly, I had to play around with the positioning equation for a while, so
		# some if it I can't explain, but most of it is straight forward.
		# All in all it's just converting from one coordinat system to another.
		sheight,swidth = pygame.display.get_surface().get_size()
		for obj in self.chunk_objects:
			xoff = int(swidth/2) + self.parent.player.x * -1
			yoff = int(sheight/2) + self.parent.player.y
			xoff+= obj.x
			yoff+= obj.y * -1
			obj.draw(self.screen,(xoff,yoff))
		pass
	class util(object):
		def blur_surf(surf,radius=3):
		    # create the original pygame surface
		    #surf = pygame.image.fromstring(, size, mode)
		    size = surf.get_size()
		    raw = pygame.image.tostring(surf,"RGBA",False)
		    # create a PIL image and blur it
		    pil_blured = PIL.Image.frombytes("RGBA", size, raw).filter(PIL.ImageFilter.GaussianBlur(radius=radius))

		    # convert it back to a pygame surface
		    filtered = pygame.image.fromstring(pil_blured.tobytes("raw", "RGBA"), size, "RGBA")
		    return filtered
class key_bindings(object):
	def __init__(self,parent):
		# right now, we won't be loading any key bindings from a user file.
		# just using the default
		self.parent = parent
		if parent.mode == 0:
			self.bindings = {
				pygame.K_ESCAPE : parent.toggle_pause
			}
		elif parent.mode == 1:
			self.bindings = {
				pygame.K_ESCAPE : parent.toggle_pause,
				pygame.K_g : parent.player.give_all
			}
		elif parent.mode == 2:
			self.bindings = {
				pygame.K_ESCAPE : parent.toggle_pause,
				pygame.K_g : parent.player.give_all
			}
	def check_all(self,event):
		# run through key bindings
		# run any functions/methods if that key is pressed
		for key in self.bindings:
			if event.key == key:
				self.bindings[key]()
class item_manager(object):
	def __init__(self,parent):
		self.minerals = self.load_minerals("minerals.json")
	def load_minerals(self,f):
		r = open(f,'r').read()
		j = json.loads(r)
		m = {}
		for i in j["all"]:
			m[i] = mineral_constructor(
				j["all"][i]["color"],
				i
				)
		return m
	class mineral_counter(object):
		def __init__(self,obj):
			self.name = obj.name
			self.color = obj.color
			self.count = 0
		def add(self,quantity):
			self.count += quantity
		def remove(self,quantity):
			self.count -= quantity
class sword_crafter(object):
	def __init__(self,parent,dimensions):
		self.parent = parent
		self.gui = parent.gui
		##self.parent.player.possesions.give(0,self.parent.item_manager.minerals["Calderite"],1)
		##self.parent.player.give_all()
		self.figurative_minerals = self.parent.player.possesions.minerals
		self.pixel_window = guiObjects.pixel_editor(self,self.gui.screen,dimensions)
		self.min_window = guiObjects.mineral_window(self,self.gui,list(self.figurative_minerals.values()))
		self.min_window.hide()
		self.load_window = guiObjects.weapon_load_window(self,self.gui.screen)
		self.load_window.hide()
	def check_mouse(self,event):
		self.min_window.try_scroll(event)
		self.load_window.check_click()
		self.pixel_window.check_click()
	def try_save(self,status):
		if status:
			self.save_weapon()
		else:
			pass
		# destroy object once it has been clicked
		self.confirms.pop("build_confirm")
	def load_popup(self):
		self.load_window.show()
	def show_conf(self):
		confirm = guiObjects.confirm(
			self.gui.screen,
			(
				int((self.gui.screen.get_width() - 500) / 2),
				int((self.gui.screen.get_width() - 200) / 2),
				500,
				200
			),
			self.parent.fonts.courb.render("Are you sure? You will loose:",False,(0,0,0)),
			self.try_save
			)
		self.confirms["build_confirm"] = confirm
	def exit(self):
		self.looping = False
		pass
	def run(self):
		# first pause the game PROGRAM so everything stops
		self.parent.pause(gui=False) 
		self.looping = True
		buttons = []
		bfont = pygame.font.SysFont("Arial",14)
		lbtn = guiObjects.button(
			self.gui.screen,
			(
				self.gui.screen.get_width() - 50 - 20,
				70,
				50,
				20
			),
			(150,150,150),
			self.load_popup,
			text=bfont.render("Load",False,(0,0,0)),
			hover=(170,170,170)
			)
		buttons.append(lbtn)
		sbtn = guiObjects.button(
			self.gui.screen,
			(
				self.gui.screen.get_width() - 50 - 20,
				100,
				50,
				20
			),
			(150,150,150),
			self.show_conf,
			text=bfont.render("Build",False,(0,0,0)),
			hover=(170,170,170)
			)
		buttons.append(sbtn)
		cbtn = guiObjects.button(
			self.gui.screen,
			(
				self.gui.screen.get_width() - 50 - 20,
				130,
				50,
				20
			),
			(150,150,150),
			self.pixel_window.clear,
			text=bfont.render("Clear",False,(0,0,0)),
			hover=(170,170,170)
			)
		buttons.append(cbtn)
		clbtn = guiObjects.button(
			self.gui.screen,
			(
				self.gui.screen.get_width() - 50 - 20,
				160,
				50,
				20
			),
			(150,150,150),
			self.exit,
			text=bfont.render("Exit",False,(0,0,0)),
			hover=(170,170,170)
			)
		buttons.append(clbtn)
		self.gui.add_event((pygame.MOUSEBUTTONDOWN,self.check_mouse))
		self.confirms = {}
		self.gui.set_cursor("editor")
		while self.looping:
			self.parent.gui.check_events(key_bindings=False)
			mx,my = pygame.mouse.get_pos()
			keys = pygame.key.get_pressed()
			if keys[pygame.K_e]:
				self.min_window.show()
			else:
				self.min_window.hide()
			# refresh minerals according to the player's possesions
			self.min_window.minerals = list(self.figurative_minerals.values())
			# clear screen
			self.gui.screen.fill((255,255,255))
			# refresh the pixel window
			self.pixel_window.refresh()
			# if the mouse is over one of the pixel/squares in the pixel window, make it lighter
			self.pixel_window.try_hover()
			# update the pixel window before rendering
			self.pixel_window.update()
			# render pixel window
			self.pixel_window.draw(self.gui.screen)
			# update mineral window before attempting to render it
			self.min_window.update()
			# attempt to draw the mineral window to the screen
			self.min_window.draw(self.gui.screen)
			# update before attempting to draw
			self.load_window.update()
			# attempt to draw it
			self.load_window.draw()
			# draw buttons
			for b in buttons:
				b.try_hover()
				b.draw()
				b.check_click()
			# render confirms
			ck = list(self.confirms.keys())
			for c in ck:
				self.confirms[c].draw()
				self.confirms[c].check_click()
			# render mouse last
			x = mx - (self.gui.cursor.get_height() / 2)
			y = my - (self.gui.cursor.get_width() / 2)
			self.gui.screen.blit(self.gui.cursor,(x,y))
			pygame.display.update()
		self.gui.set_cursor("regular")
		# lastly pause again, but with the gui. This gives the effect that it was always paused and you are simply returning to it
		self.parent.pause()
	def save_weapon(self):
		# firstly, grab array from from weapon cache
		"""
		# this sets the template
		arr = []
		for y in range(len(self.pixel_window.weapon_cache)):
			arr.append([])
			for x in range(len(self.pixel_window.weapon_cache[y])):
				if self.pixel_window.weapon_cache[y][x] != None:
					arr[y].append(True)
				else:
					arr[y].append(False)
		w = open("weapon_generated.json",'w')
		w.write(
			json.dumps(arr)
			)
		w.close()
		"""
		# operating on the array
		arr = []
		for y in range(len(self.pixel_window.weapon_cache)):
			arr.append([])
			for x in range(len(self.pixel_window.weapon_cache[y])):
				if self.pixel_window.weapon_cache[y][x] != None:
					clr = self.pixel_window.weapon_cache[y][x].color
					arr[y].append(
						(
							clr[0],
							clr[1],
							clr[2],
							255
						)
						)
					# take mineral from the user
					self.parent.player.possesions.take(0,self.pixel_window.weapon_cache[y][x],1)
				else:
					arr[y].append(
						(
							0,
							0,
							0,
							0
						)
						)	
		# now the actual saving
		img = PIL.Image.new("RGBA",(len(arr),len(arr[0])),(0,0,0,255))
		for y in range(len(arr)):
			for x in range(len(arr[y])):
				img.putpixel((x,y),arr[y][x])
		img.save("user/weapons/weapon_1.png")
		self.looping = False
class game_kernel(object):
	def log(self,msg,level="INFO",user="GAME"):
		"""If in developer mode, logs a message to the launcher window that created that initialized this class."""
		if self.mode == 1:
			# will only log stuff if in developer mode
			self.dev.log(msg,level=level,user=user)
	def __init__(self,parent,dev_window=None,mode=0):
		"""Loads a bit of stuff and logs, however it does not run any boot scripts. That method can be run by self.run_start()."""
		self.mode = mode
		self.paused = False
		#automatically change mode to 1 if a dev window is supplied
		if dev_window != None:
			self.mode = 1
			self.dev = dev_window
		self.parent = parent
		self.log("Building gui...")
		self.gui = gui(self)
		self.page = None
		self.mouse = pygame.mouse
		self.log("Loading fonts...")
		self.fonts = font_collection()
		self.log("Loading audio...")
		self.audio = audio_manager(self)
		self.log("Loading item manager...")
		self.item_manager = item_manager(self)
		self.log("Loading player...")
		self.player = new_player("Developer",self)
		# keybindings last, since they'll use methods from the object above
		self.log("Loading key bindings...")
		self.key_bindings = key_bindings(self)
	def kill_sound(self):
		"""Mutes the game."""
		self.audio.mute()
	def pause(self,gui=True):
		self.paused = True
		if gui:
			# don't change the page. Since if you do, it will halt all while loops depending on it,
			# therefore stopping the game without an actual QUIT
			#self.page = "pause"
			self.stop = False
			######
			# Defining/rendering all this stuff first makes the pause screen
			# waaaaayyy faster. If not for this pre rendering, it would lag like crazy
			######
			# old screen, blurred
			old_screen = self.gui.util.blur_surf(self.gui.screen.copy(),radius=6)
			# heght width
			sheight,swidth = pygame.display.get_surface().get_size()
			# really just a transparent grey image. Generated by PIL
			greyout = pygame.image.fromstring(PIL.Image.new("RGBA",(swidth,sheight),(50,50,50 ,128)).tobytes(),(sheight,swidth),"RGBA")
			ptext = self.fonts.pause_f.render("Paused",False,(255,255,255))
			etext = self.fonts.pause_f.render("resume",False,(255,255,255))
			px = swidth/2 - ptext.get_rect()[2]/2
			py = 40
			buttons = []
			# common height is a varaible that will set every button's height
			cmnheight = 30
			ebtn = guiObjects.button(
				self.gui.screen,
				(
					int(swidth/2 - 400/2),
					int(py + ptext.get_rect()[3] + cmnheight),
					400,
					cmnheight
				),
				(128,128,128),
				self.unpause,
				text=etext,
				hover=(200,200,200)
				)
			buttons.append(ebtn)
			qbtn = guiObjects.button(
				self.gui.screen,
				(
					int(swidth/2 - 400/2),
					int(py + ptext.get_rect()[3] + cmnheight * 2 + 10),
					400,
					cmnheight
				),
				(128,128,128),
				self.pause_quit,
				text=self.fonts.pause_f.render("Quit Game",False,(255,255,255)),
				hover=(200,200,200)
				)
			buttons.append(qbtn)
			cbtn = guiObjects.button(
				self.gui.screen,
				(
					int(swidth/2 - 400/2),
					int(py + ptext.get_rect()[3] + etext.get_rect()[3] +  cmnheight * 3 - 5),
					400,
					cmnheight
				),
				(128,128,128),
				self.start_crafter,
				text=self.fonts.pause_f.render("Start Crafter",False,(255,255,255)),
				hover=(200,200,200)
				)
			buttons.append(cbtn)
			# the background that will be continuesly rendered
			background = pygame.Surface((swidth,sheight))
			# draw the last screen, before the game was paused. This gives the effect of a "pause"
			background.blit(old_screen,(0,0))
			# render the grey image, adding to the blur effect
			background.blit(greyout,(0,0))
			# render "paused" text
			background.blit(ptext,(px,py))
			while self.paused and not self.stop:
				# check events, mainly to keep the window from "not responding"
				self.gui.check_events()
				# reset useful values
				mx,my = self.mouse.get_pos()
				clicks = pygame.mouse.get_pressed()
				# clear the screen
				self.gui.screen.fill((255,255,255))
				# render the background first
				self.gui.screen.blit(background,(0,0))
				# no if statements the game would crash, since it's shutting down mid process
				# ---------------------------------------------
				# all button functions here
				for b in buttons:
					# if mouse is over button
					b.try_hover()
					b.check_click()
					# all buttons/page elements rendered here
					b.draw()
				# ---------------------------------------------
				# render mouse last
				x = mx - (self.gui.cursor.get_height() / 2)
				y = my - (self.gui.cursor.get_width() / 2)
				self.gui.screen.blit(self.gui.cursor,(x,y))
				# update finally
				pygame.display.update()
	def unpause(self):
		self.paused = False
	def start_crafter(self):
		if not len(self.player.possesions.minerals) > 0:
			print("Oops! You don't have any minerals. Try finding some, then come back.")
		else:
			crafter = sword_crafter(self,(24,24))
			crafter.run()
	def toggle_pause(self):
		if not self.paused:
			self.pause()
		else:
			self.unpause()
	def pause_quit(self):
		# when used in the proper way,this will end the game loop without crashing the program
		self.paused = False
		self.stop = True
		self.page = None
	def run(self):
		if self.mode == 0:
			self.log("Running credits...")
			self.page = "init_credits"
			self.init_credits()
		elif self.mode == 1:
			self.log("Skipping Credits for dev mode.")
		##self.init_credits()
		self.run_start()
	def quit(self):
		"""Sets all looping variables to False, quits pygame and logs that the Game is stopping."""
		self.log("Quit event activated. Stopping game.")
		self.page = None
		if self.__dict__.__contains__("stop"):
			self.stop == True
		pygame.quit()
	def game_loop(self):
		"""Unused at this point. Really self.run_realm_explorer() is the game loop."""
		pass
	def init_credits(self):
		self.page = "init_credits"
		# text we're going to blit
		t1 = self.fonts.title_mc.render("Developed by Calder White",False,(255,255,255))
		t2 = self.fonts.title_mc.render("Music by Kevin Hu",False,(255,255,255))
		# some dimensions to help us with styling
		useless1,useless2,swidth, sheight = self.gui.screen.get_rect()
		# positions
		t1_pos = ( int((swidth - t1.get_rect()[2]) /2),sheight/2)
		t2_pos = ( int((swidth - t2.get_rect()[2]) /2),sheight/2)
		# surfaces
		ts = pygame.Surface(self.fonts.title_mc.size("Developed by Calder White"))
		ts.blit(t1,(0,0))
		# delay (this is really just for your understanding)
		# 7 is how many seconds the first portion of the music lasts
		# multiplied by 1000 to convert to miliseconds
		# divided by 255 to achive the smoothes fade in
		# divided by 2 since half the time it will be fading in and half the time it will be fading out
		delay = int(7 * 1000 / 255 / 2)
		# music
		self.audio.play_and_load_music("audio/music/tracks/theme_baseline.mp3")
		for i in range(255):
			self.gui.check_events()
			self.gui.screen.fill((0,0,0))
			ts.set_alpha(i)
			self.gui.screen.blit(ts,t1_pos)
			pygame.time.delay(delay)
			pygame.display.update()
		# delay so we can read it for a while
		# also to accomodate for the music rounding
		pygame.time.delay(7*1000 - int(7 * 1000 / 255 / 2) * 2 * 255)
		for i in range(255):
			self.gui.check_events()
			self.gui.screen.fill((0,0,0))
			ts.set_alpha(255 - i)
			self.gui.screen.blit(ts,t1_pos)
			pygame.time.delay(delay)
			pygame.display.update()
		# second message
		ts.fill((0,0,0))
		ts.blit(t2,(0,0))
		for i in range(255):
			self.gui.check_events()
			self.gui.screen.fill((0,0,0))
			ts.set_alpha(i)
			self.gui.screen.blit(ts,t2_pos)
			pygame.time.delay(delay)
			pygame.display.update()
		# delay so we can read it for a while
		# also to accomodate for the music rounding
		pygame.time.delay(7*1000 - int(7 * 1000 / 255 / 2) * 2 * 255)
		for i in range(255):
			self.gui.check_events()
			self.gui.screen.fill((0,0,0))
			ts.set_alpha(255 - i)
			self.gui.screen.blit(ts,t2_pos)
			pygame.time.delay(delay)
			pygame.display.update()
		# since this is just an animation of sorts, this function is actually done.
		# delay for dramatic affect.
		pygame.time.delay(1000)
		pass
	def run_start(self):
		"""Displays the start page"""
		# clear music
		pygame.mixer.music.stop()
		self.log("Entering Start Page",user="REALMS")
		self.page = "startup"
		self.gui.screen.fill( (255,255,255) )
		#clock = pygame.time.Clock()
		# play start music (in an endless loop)
		self.audio.play_and_load_music("audio/music/tracks/theme_melody.mp3",loops=-1)
		# mainloop
		while self.page == "startup":
			self.gui.check_events()
			self.stop = False
			# check events
			if self.stop == False:
				self.gui.screen.fill( (255,255,255) )
				mx,my = self.mouse.get_pos()
				height,width = pygame.display.get_surface().get_size()
				# load all the rectangles
				# load all the text
				# play button/text
				default_font = pygame.font.SysFont("monospace", 32,bold=True)
				play_text = default_font.render("Play",0,(0,0,0))
				x,y = self.gui.screen.get_size()
				x = int((x - play_text.get_rect()[2]) / 2)
				y=  y - (height/3.6)
				##print(mx,my)
				#use the text rectangle
				empyty1,empty2,tw,th = tuple(play_text.get_rect())
				if mx > x and mx < (x + tw) and my > y and my < (y + th):
					color = (0,128,0)
					#play_text.set_colorkey(color)
					if self.mouse.get_pressed()[0]:
						self.log("Entering Realm 1...",user="REALMS")
						self.page = "realm_1"
						self.run_realm_explorer()
						break
				else:
					color = (0,0,0)
					#play_text.set_colorkey(color)
					pass
				new_text = default_font.render("Play",0,color)
				self.gui.screen.blit(new_text,(x,y))
				# blit mouse last
				x = mx - (self.gui.cursor.get_height() / 2)
				y = my - (self.gui.cursor.get_width() / 2)
				self.gui.screen.blit(self.gui.cursor,(x,y))
				# refresh
				pygame.display.update()
	def realm_explorer_init(self):
		"""Sets up some properties for self.run_realm_explorer()"""
		if self.mode == 1:
			self.current_chunk = self.gui.chunks[0]
	def run_realm_explorer(self):
		"""Essentially the game loop."""
		# clear all music
		pygame.mixer.music.stop()
		self.page = "realm_1"
		self.stop = False
		self.realm_explorer_init()
		if self.mode == 1:
			self.current_chunk = self.gui.chunks[0]
		while self.page == "realm_1":
			##print(self.stop)
			keys = pygame.key.get_pressed()
			if not self.stop:
				self.gui.check_events()
				# clear
				self.gui.screen.fill( (255,255,255) )
				# load values
				mx,my = self.mouse.get_pos()
				sheight,swidth = pygame.display.get_surface().get_size()
				# modify player's position accordingly
				# speed modification
				self.player.check_movement()
				#print(self.player.x,self.player.y)
				# load & render background according to player's xy
				self.gui.render_floor()
				# render player
				width,height = self.player.hitbox
				# the x,y definitions look weird, but that's just because I want the player to be at zero forever
				x = (swidth / 2) - width / 2
				y = (sheight / 2) - height / 2
				pygame.draw.rect(self.gui.screen,(255,0,0),[x,y,width,height],1)
				# temporary rendering object
				self.gui.render_objects()
				# render mouse
				x = mx - (self.gui.cursor.get_height() / 2)
				y = my - (self.gui.cursor.get_width() / 2)
				self.gui.screen.blit(self.gui.cursor,(x,y))
				# finally, update
				pygame.display.update()
				self.gui.check_events()
def main(parent):
	if parent == None:
		print("Program cannot run without a launcher.")
	else:
		if parent.mode == 0:
			pass
		elif parent.mode == 1:
			if parent.run_with_errors:
				try:
					g = game_kernel(parent,dev_window=parent)
					g.run_start()
				except:
					e = sys.exc_info()
					parent.log("Exception:",level="CRITICAL",user="GAME")
					parent.log(str(e[1]),level="CRITICAL",user="GAME")
					parent.log("File: [%s]" % (str(e[2].tb_frame.f_code.co_filename)),level="CRITICAL",user="GAME")
					parent.log("Line number: [" + str(e[2].tb_lineno) + "]",level="CRITICAL",user="GAME")
					pygame.quit()
			else:
				parent.log("Beginning runtime boot.",user="GAME")
				g = game_kernel(parent,dev_window=parent)
				g.run()
			pygame.quit()
			print("Done")
		elif parent.mode == 2:
			##parent.log("Running in cheat mode.",user="GAME")
			pass