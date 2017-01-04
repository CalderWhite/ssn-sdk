import os, sys, zipfile, shutil, base64, time, platform, ctypes
def get_files(path):
     for (dirpath, _, filenames) in os.walk(path):
         for filename in filenames:
             yield os.path.join(dirpath, filename)
def get_dirs(path):
	dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
	return dirs
def remove_excluded_dirs(path,excludes):
	dirs = get_dirs(path)
	for d in dirs:
		remove_excluded_dirs(path + "/" + d,excludes)
	for e in excludes:
		if dirs.__contains__(e):
			shutil.rmtree(path + "/" + e)
def remove_excluded_files(path,excludes,suffixes):
	f = get_files(path)
	for i in f:
		fn = i.split("\\")[-1]
		if excludes.__contains__(fn):
			os.remove(i)
		elif suffixes.__contains__(i.split(".")[-1]):
			os.remove(i)
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
def main():
	begin = time.time()
	ops = platform.system()
	allowed_os = ["Windows"]
	if ops == "Windows":
		usage = """Usage:
	%s [directory] [version]
		""" % (sys.argv[0].split("\\")[-1].split(".")[0])
		operating_system_dist = "WIN"
		excludes = {
			"dirs" : [
				"__pycache__",
				"GMK"
			],
			"files" : [
				"Sword_Smith_Now_logs.log",
				"README.md",
				"Thumbs.db",
				"test.py"
			],
			"suffixes" : [
				"py",
				"pyw"
				"pyc"
			]
		}
		mainfilename = "launcher.py"
		appname = "Sword Smith Now"
		endname = "Sword_Smith_Now.exe"
		argz = sys.argv[1:]
		dash = []
		ddash = []
		commands = []
		for i in argz:
			if i[0:2] == "--":
				ddash.append(i)
			elif i[0] == "-":
				dash.append(i)
			else:
				commands.append(i)
		if len(commands) < 2:
			print(usage)
		elif commands[1][0].lower() != "v" and commands[1][0].lower() != "a" and commands[1][0].lower() != "b":
			print("The first character of the version argument is not a valid identifier! An example version is v1.0.0 or Alpha 0.2.7 or Beta 9.3.2")
		else:
			if not os.path.exists("./dist"):
				print("Creating \"./dist\" directory...")
				os.mkdir("./dist")
			print("Creating build directory...")
			nn = commands[0].split("/")[-1].replace(" ","_")
			bigname = "%s_%s_%s" % (
				appname.replace(" ","_"),
				operating_system_dist,
				commands[1].replace(" ","_")
			)
			icon_path = commands[0] + "/images/icon2.ico"
			init_build = os.path.exists("./build")
			if os.path.exists("./dist/%s_%s" % (operating_system_dist,nn)) or os.path.exists("./dist/%s" % bigname):
				print("ERROR: There is already a version [%s]" % commands[1])
			else:
				ctypes.windll.user32.MessageBoxW(0, "NOTE: The average build time is 300 seconds! This WILL take a while...", "Sword Smith Now Builder", 0)
				print("Running on %s %s %s" % (ops,platform.release(),platform.architecture()[0]))
				cmnd = "py ./pyinstaller/pyinstaller.py \"%s/%s\" --onefile -i %s" % (commands[0],mainfilename,icon_path)
				print("Running %s" % cmnd)
				os.system(cmnd)
				print("Removing build directory, now that standalone has been created.")
				shutil.rmtree("./build/" + mainfilename.split(".")[0])
				if os.path.exists("./build/" + nn):
					shutil.rmtree("./build/" + nn)
				print("Copying files from source...")
				shutil.copytree(commands[0],"build/" + nn)
				print("Removing excludes...")
				# add the file that has been converted to .exe to excludes
				excludes["files"].append(mainfilename)
				# directories first
				remove_excluded_dirs("./build/" + nn,excludes["dirs"])
				remove_excluded_files(
					"./build/" + nn,
					excludes["files"],
					excludes["suffixes"]
					)
				print("Moving standalone executable to build directory.")
				try:
					shutil.move("dist/" + mainfilename.split(".")[0] + ".exe","./build/%s" % (nn))
				except FileNotFoundError:
					print("THERE WAS AN ERROR COMPILING THE PYTHON SOURCE")
				else:
					# rename file
					os.rename("./build/%s/%s" % (nn,mainfilename.split(".")[0] + ".exe"),"./build/%s/%s" % (nn,endname))
					# create dist directory
					os.mkdir("./dist/" + bigname)
					zipf = zipfile.ZipFile(
						'./dist/%s/source.zip' % bigname,
						'w',
						zipfile.ZIP_DEFLATED
					)
					print("Zipping %s" % ("./build/" + nn))
					os.chdir("./build/%s" % nn)
					zipdir(
						".",
						zipf
					)
					zipf.close()
					os.chdir("../..")
				installer_name = nn + "_installer"
				print("Reading install_template.py ...")
				r = open("install_template",'r').read().format(
					"source.zip",
					bigname,
					allowed_os,
					nn,
					"images/icon.ico",
					endname
					)
				with open("dist/%s/%s.py" % (bigname,installer_name),'w') as w:
					w.write(r)
				install_compile_cmnd = "py pyinstaller/pyinstaller.py dist/%s/%s.py --onefile -i %s" % (bigname,installer_name,icon_path)
				print("Running %s" % install_compile_cmnd)
				os.system(install_compile_cmnd)
				shutil.move("./dist/%s.exe" % (installer_name),"./dist/%s/%s.exe" % (bigname,installer_name))
				# delete files that we once used
				print("Cleaning up loose files...")
				if not init_build:
					shutil.rmtree("./build")
				else:
					shutil.rmtree("./build/" + installer_name)
					shutil.rmtree("./build/" + nn)
				shutil.rmtree("./dist/%s/__pycache__" % bigname)
				os.remove("./dist/%s/%s" % (bigname,installer_name + ".py"))
				# iexpress package bundle creation
				r = open("package_template",'r').read()
				r = r.format(
					commands[0],
					commands[1],
					os.getcwd() + "\\dist\\%s\\%s" % (bigname,installer_name + ".exe"),
					installer_name + ".exe",
					os.getcwd() + "\\dist\\%s" % bigname
					)
				w = open(installer_name + ".SED",'w')
				w.write(r)
				w.close()
				# create the final product
				print("Bundling installer with source...")
				os.system("iexpress /N %s" % (installer_name + ".SED"))
				# remove source from the dist output, since it is now inside the installer
				print("Cleaning up loose files...")
				os.remove("dist/%s/source.zip" % bigname)
				os.remove("./%s.SED" % installer_name)
				os.remove("./%s.spec" % installer_name)
				os.remove("./%s.spec" % mainfilename.split(".")[0])
				print("Finished! Your installation executable is in ./dist/%s" % bigname)
				end = time.time()
				elapsed = end - begin
				print("%s Seconds elapsed" % elapsed)
	else:
		print("Operating system [%s] not supported, sorry." % ops)
		print("Supported Operating Systems:\n%s" % allowed_os)
if __name__ == '__main__':
	main()