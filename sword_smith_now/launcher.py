import logging,json, tkinter, time, threading, sys, datetime, imp, os, gc
from tkinter import ttk

class gui(object):
	def __init__(self):
		self.tk = tkinter.Tk()
		sw = self.tk.winfo_screenwidth()
		sh = self.tk.winfo_screenheight()
		ww = 760
		wh = 490
		x = int(sw / 2) - int(ww/2)
		y = int(sh / 2) - int(wh / 2)
		self.tk.geometry("%sx%s+%s+%s" % (ww,wh,x,y))
		self.tk.resizable(width=False, height=False)
		self.tk.title("Launching...")
		#log_frames 'n' stuff
		self.nb = ttk.Notebook(self.tk)
		self.nb.grid()
		self.log_frame = ttk.Frame()
		self.nb.add(self.log_frame,text="Log")
		# text
		self.log_field = tkinter.Text(self.log_frame,height=25,width=95 )
		self.log_text = ""
		self.log_field.configure(state=tkinter.DISABLED)
		self.log_field.grid(row=0)
		# future field, Work in Progress
		self.profile_frame = ttk.Frame()
		self.nb.add(self.profile_frame,text="Profile")

		##self.log_field.pack()
		pass
class launcher(object):
	def __init__(self,mode,log_file,info_file,initial_gui=False):
		if mode == 0 or mode == 1 or mode == 2:
			# mode index:
			# 0 : normal mode; nothing special.
			# 1 : developer mode; will check modules, as if it were being run by the python interperator instead of .exe format.
			# 2 : cheats mode; nothing yet, going to be a version of dev mode to test bosses with hacks.
			self.mode = mode
			##print("Running log configuration.\nAll other logging/debugging messages will be sent to the specified log file once configured.")
			self.game_info_name = "ssn/" + info_file
			self.get_game_file()
			# clear the log file
			with open(log_file,'w') as f:
				f.truncate()
			logging.basicConfig(filename=log_file,level="INFO")
			self.game_name = "GAME NAME IS UNKNOWN"
			self.initial_gui = initial_gui
			self.allow_run = None
			self.waiting = True
		else:
			raise Exception("Launch mode [%s] not supported" % mode)
		pass
	def try_launch(self):
		if self.allow_run:
			self.log("--------------------------------------------------------")
			self.log("Launching [%s]..." % self.game_name)
			# reload runtime so that all code changes are implimented
			import runtime
			runtime = imp.reload(runtime)
			r = open(self.game_info_name,'r').read()
			self.info = json.loads(r)
			runtime.main(self)
			self.log("Game has stopped.")
			self.log("Collecting the garbage...")
			gc.collect()
			self.log("Running main loop until user closes.")
			##if self.mode == 1:
			##	self.log("Restarting self since in developer mode.")
			##	os.system("start " + __file__)
			##	sys.exit(0)
			if self.initial_gui:
				self.waiting_loop()
		elif self.allow_run == False:
			self.log("There were errors during checks, no launch may be run.",level="ERROR")
		elif self.allow_run == None:
			self.log("Launch was attempted by user, but all checks have not yet been completed.",level="WARNING")
			pass
	def load(self):
		if self.initial_gui:
			logging.log(logging.INFO,"Running Launcher with gui.")
			#creating and defining window
			self.gui = gui()
			# start the mainloop thread
			self.gui.tk.update()
			self.log("Running launcher in gui...")
			s = ttk.Style()
			s.configure('my.TButton', font=("Arial", 12,"bold"),padding=17,width=25,justify="center")
			self.play_b = ttk.Button(self.gui.log_frame, text="Play", command=self.try_launch,style="my.TButton")
			self.play_b.grid(row=1)
			self.log("Time: " + str(datetime.datetime.now()))
			self.log("Setting launcher icon.")
			#load the ico version instead of the png. This just seems to work
			self.gui.tk.iconbitmap(default='images/icon.ico')
			checks = self.do_checks()
			if checks:
				self.log("Load was succesful.")
				self.allow_run = True
			else:
				self.allow_run = False
			self.waiting_loop()
		else:
			self.log("Running launcher in non-gui mode.")
			self.log("Time: " + str(datetime.datetime.now()))
			checks = self.do_checks()
			if checks:
				self.log("Load was succesful.")
				self.allow_run = True
				def ask_launch():
					x = input("Launch?(Y/N):")
					y = recive_input(x)
					return y
				def recive_input(x):
					x = x.upper()
					if x == "Y":
						return True
					elif x == "N":
						self.log("Succesful load, user decided not to launch.")
					else:
						self.log("Got answer that was neither \"Y\" or \"N\". Asking again...")
						print("Please Enter either Y or N")
						ask_launch()
				z = ask_launch()
				if z:
					self.try_launch()

			else:
				self.log("Stopping launch, shutting down program...")
				self.allow_run = False
		self.log("--------------------------------------------------------")
	def waiting_loop(self):
		"""Just wait for some user input"""
		self.gui.tk.mainloop()
	def get_game_file(self):
		##self.log("Loading the game info file [%s]..." % (self.game_info_name))
		r = open(self.game_info_name,'r').read()
		info = json.loads(r)
		try:
			x = info["paths"]["."]
		except:
			raise Exception("Game info [paths][.] is missing.")
		else:
			os.chdir(info["paths"]["."])
	def log(self,msg,level="INFO",user="LAUNCHER"):
		logging.log(logging.__getattribute__(level),msg)
		if self.initial_gui:
			self.gui.log_field.pack_forget()
			self.gui.log_field = tkinter.Text(self.gui.log_frame,height=25,width=95 )
			self.gui.log_text = self.gui.log_text + "[" + user +  "]:[" + level + "]: " + msg + "\n"
			##print(self.gui.log_text)
			self.gui.log_field.insert(tkinter.END,self.gui.log_text)
			self.gui.log_field.grid(row=0)
			self.gui.log_field.configure(state=tkinter.DISABLED)
			##self.gui.log_field.pack()
			self.gui.tk.update()
			self.gui.log_field.see(tkinter.END)
		pass
	def module_checklist(self):
		self.log("Loading the game info file [%s]..." % (self.game_info_name))
		r = open(self.game_info_name,'r').read()
		info = json.loads(r)
		try:
			x = info["paths"]
			x = info["name"]
		except IndexError:
			self.log("Couldn't find \"paths\" in game info file (%s)" % self.game_info_name,level="ERROR")
			raise Exception("Couldn't find \"paths\" in game info file (%s)" % self.game_info_name)
		else:
			try:
				self.game_name = info["name"] + " " + info["version"]
			except:
				self.game_name = info["name"] + " Alpha <0.3.0"
			if self.initial_gui:
				self.gui.tk.title(self.game_name + " Launcher")
			self.log("Loading requirements list.")
			r = open(info["paths"]["requirements"],'r').read()
			requirez = json.loads(r)
			if self.mode == 1:
				self.log("Checking required modules for DEV MODE...")
				for i in requirez["dev"]:
					try:
						__import__(i)
					except:
						self.log("No [%s] module, which is required." % i,level="ERROR")
			else:
				self.log("Checking required modules...")
				for i in requirez["vanilla"]:
					try:
						__import__(i)
					except:
						self.log("No [%s] module, which is required." % i,level="ERROR")
			self.log("All required modules present.")
	def do_checks(self):
		if self.mode == 0:
			print("CONSUMER VERSION IS NOT YET SUPPORTED.")
		elif self.mode == 1:
			self.log("Running launch. Mode : 1")
			try:
				self.module_checklist()
			except:
				self.log("Hit error in developer mode [mode 1]. While running %s" % (self.__class__.__name__ + ".module_checklist()"),level="CRITICAL")
				self.log(str(sys.exc_info()))
				return False
			else:
				return True
		elif self.mode == 2:
			pass
def main():
	dash = []
	ddash = []
	commands = []
	for i in sys.argv[1:]:
		if i[0:2] == "--":
			ddash.append(i)
		elif i[0] == "-":
			dash.append(i)
		else:
			command.append(i)
	if len(sys.argv[1:]) == 0:
		l = launcher(0,"Sword_Smith_Now_logs.log","game_info.json",initial_gui=True)
		l.load()
	"""
	accepted = {
		"-t" : [0,"Sword_Smith_Now_logs.log","game_info.json",False],
		"--terminal-only" : [0,"Sword_Smith_Now_logs.log","game_info.json",False],
		"-d" : [1,"Sword_Smith_Now_logs.log","game_info.json",True],
		"--dev-mode" : [1,"Sword_Smith_Now_logs.log","game_info.json",True],
		"-c" : [2,"Sword_Smith_Now_logs.log","game_info.json",True],
		"--cheats" : [2,"Sword_Smith_Now_logs.log","game_info.json",True]
	}"""
	if commands.__contains__("help") or dash.__contains__("-h") or ddash.__contains__("--help") or commands.__contains__("/?"):
		t = " -t, --terminal-only 	Disables the gui pop up for the launcher, and instead uses the terminal."
		d = " -d, --dev-mode		Launches in dev mode. Read more in the dev manual."
		c = " -c, --cheats		Launches in a version of dev mode with cheats."
		descriptions = [t,d,c]
		ptext = "\n".join(descriptions)
		print(ptext)
	elif len(commands) == 0:
		m = 0
		log = "Sword_Smith_Now_logs.log"
		info = "game_info.json"
		display = True
		r = True
		if dash.__contains__("-t") or ddash.__contains__("--terminal-only"):
			display = False
		if dash.__contains__("-d") or ddash.__contains__("--dev-mode"):
			m = 1
		if dash.__contains__("-c") or ddash.__contains__("--cheats"):
			m = 2
		if ddash.__contains__("-r") or ddash.__contains__("--run-without-errors"):
			r=False
		l = launcher(m,log,info,initial_gui=display)
		l.run_with_errors = r
		l.load()
	
if __name__ == '__main__':
	##launch = launcher(1,"Sword_Smith_Now_logs.log","game_info.json",initial_gui=True)
	##launch.load()
	main()
