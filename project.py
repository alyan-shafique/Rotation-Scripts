#!usr/bin/env python

###Python script to configure multiple interfaces at once from yml file
###Gets arguments from user input to SSH using paramiko into nexus switch/run ansible playbook
###Verifies configs are defaulted and prints output into output.txt file

import paramiko
import socket
import getpass
import yaml
from subprocess import call

def main():
	#Get IP Address, Username, Password for SSH
	#Get playbook filename for ansible-playbook
	ip = raw_input("Enter IP Address: ")
	username = raw_input("Username: ")
	password = getpass.getpass("Password: ")
	playbook = raw_input("Playbook File: ")

	#Make linux command to run ansible playbook
	call(["ansible-playbook", playbook])

	#Open/read playbook file to access "with_items" module
	#Print error message if playbook file does not exist
	try:
		with open(playbook, 'r') as f:
			doc = yaml.load(f)
	except IOError:
		print "File " + playbook + " does not exist."
		return

	#Print error message if "with_items" module does not exist
	try:
		with_items = doc[0]['tasks'][1]['with_items']
	except:
		print "with_items module does not exist."
		return

	#Use Paramiko to SSH into Nexus 9000 switch
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy())
		ssh.connect(ip,username = username,password = password)
	except paramiko.AuthenticationException:
		print "Failed to log into switch. Double check username/password and IP Address."
		return
	except socket.error:
		print "Socket Error."
		#return

	#Create output file to place results
	output = open('output.txt', 'w') 

	#Iterate over with_items list to run commands in Nexus switch
	for item in with_items:
		stdin,stdout,stderr = ssh.exec_command( 'show run interface ' + item )
		out = [line for line in stdout.readlines()]

		#Write output to file
		for line in out:
			output.write(line)

if __name__ == '__main__':
	main()