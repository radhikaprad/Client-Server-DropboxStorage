import socket
import sys
import os
import getpass
import threading

host = "127.0.0.1"
port = 5012
username=""
user_pass=""
USER_FOLDER_PATH = "/Users/radhikamanivannan/Desktop/userfolders/"
TIMER_TIME_SEC = 20.0
THREAD_RUN = True

def checkupdates():
	if THREAD_RUN == True:	
		s = socket.socket()
		s.connect((host,port))
		option_username =  "5," + username
		s.send(option_username)
		data=s.recv(1024)

		fileinfo = data.split(",")
		localfiles=os.listdir(USER_FOLDER_PATH+username)
		# print "files",fileinfo
		if len(fileinfo) != 0:
			for i in range(0,len(fileinfo)-1,3):
				name=fileinfo[i]
				size=int(fileinfo[i+1])
				date=int(fileinfo[i+2])
				if name in localfiles:
					localsize=os.path.getsize(USER_FOLDER_PATH+username+"/"+name)
					localdatemodified=os.path.getmtime(USER_FOLDER_PATH+username+"/"+name)
					
					if size != localsize:
						s.send("sendingfile"+","+name+","+str(localsize))
						with open(USER_FOLDER_PATH+username+"/"+name, "rb") as f:
							bytesToSend = f.read(1024)
							s.send(bytesToSend)
							while bytesToSend != "":
								bytesToSend = f.read(1024)
								s.send(bytesToSend)
							# print ("Background synchronising file : ",name)
				else:
					s.send("filenotavailable"+","+name+",")
					s.recv(1024)

		for localfilename in localfiles:
			if localfilename not in fileinfo:
				if not localfilename.startswith('.'):
					localsize=os.path.getsize(USER_FOLDER_PATH+username+"/"+localfilename)
					s.send("sendingfile"+","+localfilename+","+str(localsize))
					with open(USER_FOLDER_PATH+username+"/"+localfilename, "rb") as f:
						bytesToSend = f.read(1024)
						s.send(bytesToSend)
						while bytesToSend != "":
							bytesToSend = f.read(1024)
							s.send(bytesToSend)
						# print ("Background synchronising file : ",localfilename)

		s.close()
		threading.Timer(TIMER_TIME_SEC,checkupdates).start() # Create thread again for sync op 

def main():
	option = raw_input("1.Download\n2.Upload\n3.Rename\n4.Delete\n5.Exit\nEnter one of above option:")
	option_username = option + "," + username

	# Create socket and connect for this particular operation
	s = socket.socket()
	s.connect((host,port))

	if option == "1":
		s.send(option_username)
		filename = raw_input("Filename? -> ")
		s.send(filename)
		data = s.recv(1024)
		# print data
		exist,size,login=data.split(",")
		print ("values",exist,size,login)
		if str(data[:6]) in exist:
			filesize = int(size)
			message = raw_input("File Exists, " + str(filesize) + " Download?  (Y/N) -> ")
			if message == "Y":
				s.send("OK")
				with open(USER_FOLDER_PATH+login+"/"+filename,"w") as f:
					data = s.recv(1024)
					totalRecv = len(data)
					f.write(data)
					while int(totalRecv) < filesize:
						data = s.recv(1024)
						totalRecv += len(data)
						f.write(data)
				print "Download Complete"
		else:
				print "File does not exist!"

	elif option == "2":
		s.send(option_username) # Msg #2.1
		filename = raw_input("Filename? -> ")
		print USER_FOLDER_PATH+username+"/"+filename
		if os.path.isfile(USER_FOLDER_PATH+username+"/"+filename):
			s.send("EXISTS," + str(os.path.getsize(USER_FOLDER_PATH+username+"/"+filename)) + "," + filename) # Msg #2.2 (EXISTS keyword, File Size, File Name)
			print ("Uploading ", filename)
			with open(USER_FOLDER_PATH+username+"/"+filename, "rb") as f:
				bytesToSend = f.read(1024)
				s.send(bytesToSend)
				while bytesToSend != "":
					bytesToSend = f.read(1024)
					s.send(bytesToSend)
				print "Upload Complete"
		else:
				print "File does not exist!"

	elif option == "3":
		s.send(option_username)
		filename = raw_input("Filename? -> ")
		s.send(filename)
		data = s.recv(1024)
		if data == "EXISTS":
			newname = raw_input("Enter the new filename -> ")
			s.send(newname)
			print "Done"
		else:
			print "File does not exist!"
		

	elif option == "4":
		s.send(option_username)
		filename = raw_input("Filename? -> ")
		
		s.send(filename)
		data = s.recv(1024)
		if data == "EXISTS":
			message = raw_input("Are you sure?  (Y/N) -> ")
			s.send(message)
			data = s.recv(1024)
			# print data
		else:
			print "File does not exist!"

	elif option == "5":
		print("Exiting app...")
		s.close()
		THREAD_RUN = False
		sys.exit(0)

	else:
		print ("Invalid option")
	s.close()

					
if __name__ == '__main__':
	# Create dictionary to store uploaded file info [File Name -> Size in bytes and Modified Date]

	while True:	
		s = socket.socket()
		s.connect((host,port))

		option = raw_input("1.Login\n2.Register\n3.Exit\nEnter one of above option:")

		if (int(option)==1):
			username = raw_input("Enter you username : ")
			password = getpass.getpass()
		elif (int(option)==2):
			username = raw_input("Create a username : ")
			password = getpass.getpass()
		elif (int(option)==3):
			print "Exiting application"
			s.close()
			THREAD_RUN = False
			sys.exit(0)

		user_pass="0,"+username+","+password+","+option
		s.send(user_pass)
		ack=s.recv(1024)
		s.close()
		print (ack)
		if (ack in "login ok" or ack in "user created"):
			print ("Logged in")
			checkupdates()
			while True:
				main()

		elif (ack in "username exists"):
			print ("Enter a different username")
		elif (ack in "incorrect login"):
			print ("Login and password incorrect")

	
		