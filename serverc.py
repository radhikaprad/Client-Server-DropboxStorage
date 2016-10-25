import socket
import threading
import os
import sys
import atexit
import glob

USER_FOLDER_PATH = "/Users/radhikamanivannan/Desktop/serverfolders/"
usercredentialfile="usercredential.txt"
def fileOps(name, sock,usernames):
	# print usernames

	data = sock.recv(1024) # First message i.e. the (option index, username)
	# print (data)
	initialmsg=data.split(",")
	if (len(initialmsg) < 2):
		sock.close()
		return

	option = initialmsg[0]
	loginuser = initialmsg[1]
	personal_directory=USER_FOLDER_PATH+loginuser
	
	if option == "0":
		login = loginuser
		passw = initialmsg[2]
		val = initialmsg[3]
		# print "login : ",login,passw,val

		if int(val)==1:
			if str(login) in usernames:
				print (usernames[login])
				if str(passw) in usernames[login]:
					sock.send("login ok")
				else:
			 		sock.send("incorrect login")
			else:
			 	sock.send("incorrect login")

		elif int(val)==2:
			usernames[login]=passw
			if not os.path.exists(personal_directory):
				os.makedirs(personal_directory)
				sock.send("user created")
				with open(USER_FOLDER_PATH+usercredentialfile,"a") as f:
					credential="\n"+login+":"+passw
					f.write(credential)
					f.close()
			else:
				sock.send("username exists")
		else:
			sock.send("incorrect login")

		sock.close()

	if option == "1":
		filename = sock.recv(1024)
		
		if os.path.isfile(USER_FOLDER_PATH+loginuser+"/"+filename):
			# print "filename : ",USER_FOLDER_PATH+loginuser+"/"+filename
			sock.send("EXISTS,"+str(os.path.getsize(USER_FOLDER_PATH+loginuser+"/"+filename))+","+loginuser)
			userResponse = sock.recv(1024)
			print userResponse
			filename=USER_FOLDER_PATH+loginuser+"/"+filename
			if userResponse in "OK":
				with open(filename, "r") as f:
					bytesToSend = f.read(1024)
					sock.send(bytesToSend)
					while bytesToSend != "":
						bytesToSend = f.read(1024)
						sock.send(bytesToSend)
			else:
				sock.send("ERR")
		
			sock.close()
		else:
			sock.send("ERR")

	elif option == "2":
		data = sock.recv(1024) # Msg #2.2
		# print ("first command",data)
		flag,filesize,filename=data.split(",")
		if str(flag) in "EXISTS":
			# print "filesize : ",filesize
			# print ("Received FileName : ", filename)
			filename=personal_directory+"/"+filename
			data = sock.recv(1024) # Msg #2.4
			totalRecv = len(data)
			# print ("data",data)
			if not os.path.exists(filename):
				# print filename
				with open(filename,'wb') as f:
					f.write(data)
					while int(totalRecv) < int(filesize):
						data = sock.recv(1024)
						totalRecv += len(data)
						f.write(data)

			sock.close()
		else:
			print "ERR"

	elif option == "3":
		filename = sock.recv(1024)
		print USER_FOLDER_PATH+loginuser+"/"+filename
		if os.path.isfile(USER_FOLDER_PATH+loginuser+"/"+filename):
			sock.send("EXISTS")
			newname = sock.recv(1024)
			print "new file",USER_FOLDER_PATH+loginuser+"/"+newname
			os.rename(USER_FOLDER_PATH+loginuser+"/"+filename, USER_FOLDER_PATH+loginuser+"/"+newname)
			sock.close()
		else:
			sock.send("ERR")

	elif option == "4":
		filename = sock.recv(1024)
		if os.path.isfile(USER_FOLDER_PATH+loginuser+"/"+filename):
			sock.send("EXISTS")
			message = sock.recv(1024)
			if message == "Y":
				os.remove(USER_FOLDER_PATH+loginuser+"/"+filename)
				sock.send("Done")
				sock.close()
				
			else:
				pass
		else:
			sock.send("ERR")

	elif option =="5":
		files=os.listdir(USER_FOLDER_PATH+loginuser)
		
		# filename,filesize,datamodified
		file=""
		for i in files:
			if not i.startswith('.'):
				name=os.path.basename(USER_FOLDER_PATH+loginuser+"/"+i)
				size=os.path.getsize(USER_FOLDER_PATH+loginuser+"/"+i)
				datemodified=os.path.getmtime(USER_FOLDER_PATH+loginuser+"/"+i)
				file += name+","+str(size)+","+str(int(datemodified))+","
		# print ("FileList: ", file)
		sock.send(file)
		data=sock.recv(1024)
		if len(data) != 0:
			
			data=data.split(",")

			if data[0] in "sendingfile":
				filedata=sock.recv(1024)
				totalRecv = len(filedata)
				with open(USER_FOLDER_PATH+loginuser+"/"+data[1],'wb') as f:
					f.write(filedata)
					# print data[2]
					while int(totalRecv) < int(data[2]):
						filedata = sock.recv(1024)
						totalRecv += len(filedata)
						f.write(filedata)
			elif data[0] in "filenotavailable":
				filename = data[1]
				if os.path.isfile(USER_FOLDER_PATH+loginuser+"/"+filename):
					os.remove(USER_FOLDER_PATH+loginuser+"/"+filename)
				sock.send("Done")

		sock.close()


def main():
	host = "127.0.0.1"
	port = 5012
	usernames={}
	
  
  	try:
		s = socket.socket()
		s.bind((host,port))
		s.listen(5)
		print "Server started."

		# Write a function to read folders and fie info in USER_FOLDER_PATH foler and build dictionary
		with open(USER_FOLDER_PATH+usercredentialfile,"r") as f:
			data=f.read()
		data=data.split("\n")
		for i in data:
			key,val=i.split(":")
			usernames[key]=val
		# print usernames

		while True:
			conn, address = s.accept()
			print "Client connected ip:<" + str(address) + ">"
			t = threading.Thread(target = fileOps, args = ("myThread", conn,usernames))
			t.start()
  	except (KeyboardInterrupt, SystemExit):
  		print("Closing app.. Bye Bye")
  		s.close()
  		sys.exit(0)

if __name__ == "__main__":
	main()